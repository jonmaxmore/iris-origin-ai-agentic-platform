# 🚀 FastAPI Project Management Services

**Project Management API Implementation**  
**Technology**: Python + FastAPI + SQLAlchemy + PostgreSQL  
**Research Basis**: Enterprise patterns from Salesforce, Microsoft Dynamics, HubSpot

---

## 📋 **Project Management Service Architecture**

### **🔄 Service Layer Design:**

```python
# services/project_management.py - Enterprise Project Management Service
from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from fastapi import HTTPException, status
from datetime import datetime, timezone, date, timedelta
import uuid
import json
import logging
from dataclasses import dataclass

from ..models.project import (
    ProjectTemplate, ProjectExtended, ProjectMetric, 
    ProjectLifecycleEvent, ProjectCustomization, ProjectTag,
    ProjectTagAssignment, ProjectPerformanceSnapshot,
    ProjectPhase, MetricType, MetricStatus
)
from ..models.user import User, Organization, ProjectMembership
from ..schemas.project import (
    ProjectTemplateCreate, ProjectTemplateUpdate,
    ProjectCreate, ProjectUpdate, ProjectResponse,
    ProjectMetricCreate, ProjectMetricUpdate,
    ProjectCustomizationCreate, ProjectTagCreate
)
from ..core.security import get_current_user
from ..core.logging import get_logger

logger = get_logger(__name__)

@dataclass
class ProjectStats:
    """Project statistics summary"""
    total_projects: int = 0
    active_projects: int = 0
    completed_projects: int = 0
    avg_health_score: float = 0.0
    avg_completion: float = 0.0

class ProjectTemplateService:
    """Service for managing project templates"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_templates(
        self,
        category: Optional[str] = None,
        industry: Optional[str] = None,
        complexity: Optional[str] = None,
        is_featured: Optional[bool] = None,
        is_public: Optional[bool] = True,
        skip: int = 0,
        limit: int = 50
    ) -> List[ProjectTemplate]:
        """Get project templates with filtering"""
        
        query = self.db.query(ProjectTemplate).filter(
            ProjectTemplate.is_active == True
        )
        
        # Apply filters
        if category:
            query = query.filter(ProjectTemplate.category == category)
        if industry:
            query = query.filter(ProjectTemplate.industry == industry)
        if complexity:
            query = query.filter(ProjectTemplate.setup_complexity == complexity)
        if is_featured is not None:
            query = query.filter(ProjectTemplate.is_featured == is_featured)
        if is_public is not None:
            query = query.filter(ProjectTemplate.is_public == is_public)
        
        # Order by usage and rating
        query = query.order_by(
            desc(ProjectTemplate.is_featured),
            desc(ProjectTemplate.avg_rating),
            desc(ProjectTemplate.usage_count)
        )
        
        return query.offset(skip).limit(limit).all()
    
    def get_template(self, template_id: uuid.UUID) -> Optional[ProjectTemplate]:
        """Get specific project template"""
        return self.db.query(ProjectTemplate).filter(
            ProjectTemplate.template_id == template_id,
            ProjectTemplate.is_active == True
        ).first()
    
    def create_template(
        self, 
        template_data: ProjectTemplateCreate,
        current_user: User
    ) -> ProjectTemplate:
        """Create new project template"""
        
        # Check if slug already exists
        existing = self.db.query(ProjectTemplate).filter(
            ProjectTemplate.template_slug == template_data.template_slug
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Template slug already exists"
            )
        
        # Create template
        db_template = ProjectTemplate(
            **template_data.dict(),
            created_by=current_user.user_id
        )
        
        self.db.add(db_template)
        self.db.commit()
        self.db.refresh(db_template)
        
        logger.info(f"Template created: {db_template.template_id} by user {current_user.user_id}")
        return db_template
    
    def update_template(
        self,
        template_id: uuid.UUID,
        template_data: ProjectTemplateUpdate,
        current_user: User
    ) -> Optional[ProjectTemplate]:
        """Update project template"""
        
        template = self.get_template(template_id)
        if not template:
            return None
        
        # Update fields
        for field, value in template_data.dict(exclude_unset=True).items():
            setattr(template, field, value)
        
        template.updated_at = datetime.now(timezone.utc)
        
        self.db.commit()
        self.db.refresh(template)
        
        logger.info(f"Template updated: {template_id} by user {current_user.user_id}")
        return template
    
    def increment_template_usage(self, template_id: uuid.UUID) -> bool:
        """Increment template usage count"""
        template = self.get_template(template_id)
        if template:
            template.increment_usage(self.db)
            return True
        return False

class ProjectLifecycleService:
    """Service for managing project lifecycle"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_project_from_template(
        self,
        template_id: uuid.UUID,
        project_data: ProjectCreate,
        org_id: uuid.UUID,
        current_user: User
    ) -> ProjectExtended:
        """Create project from template"""
        
        # Get template
        template_service = ProjectTemplateService(self.db)
        template = template_service.get_template(template_id)
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        # Create project
        db_project = ProjectExtended(
            project_name=project_data.project_name,
            project_slug=project_data.project_slug,
            description=project_data.description,
            org_id=org_id,
            template_id=template_id,
            project_phase=ProjectPhase.SETUP,
            project_settings=template.default_settings,
            ai_config=template.default_ai_config,
            created_by=current_user.user_id
        )
        
        self.db.add(db_project)
        self.db.flush()  # Get project ID
        
        # Create initial lifecycle event
        self._create_lifecycle_event(
            project_id=db_project.project_id,
            event_type="created",
            event_name="Project Created",
            description=f"Project created from template: {template.template_name}",
            event_data={
                "template_id": str(template_id),
                "template_name": template.template_name,
                "initial_phase": ProjectPhase.SETUP
            },
            triggered_by=current_user.user_id
        )
        
        # Apply default roles and permissions from template
        self._setup_default_roles(db_project, template, current_user)
        
        # Increment template usage
        template_service.increment_template_usage(template_id)
        
        self.db.commit()
        self.db.refresh(db_project)
        
        logger.info(f"Project created: {db_project.project_id} from template {template_id}")
        return db_project
    
    def transition_project_phase(
        self,
        project_id: uuid.UUID,
        new_phase: ProjectPhase,
        current_user: User,
        reason: Optional[str] = None
    ) -> ProjectExtended:
        """Transition project to new phase"""
        
        project = self.db.query(ProjectExtended).filter(
            ProjectExtended.project_id == project_id
        ).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Validate transition
        if not self._is_valid_phase_transition(project.project_phase, new_phase):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid phase transition from {project.project_phase} to {new_phase}"
            )
        
        # Store previous state
        previous_phase = project.project_phase
        
        # Update project phase
        project.project_phase = new_phase
        project.last_activity_at = datetime.now(timezone.utc)
        
        # Handle special phase transitions
        if new_phase == ProjectPhase.ARCHIVED:
            project.archived_at = datetime.now(timezone.utc)
            project.archived_by = current_user.user_id
        elif new_phase == ProjectPhase.ACTIVE:
            # Calculate completion percentage for active projects
            project.completion_percentage = project.calculate_completion_percentage(self.db)
        
        # Create lifecycle event
        self._create_lifecycle_event(
            project_id=project_id,
            event_type="phase_transition",
            event_name=f"Phase Changed: {previous_phase} → {new_phase}",
            description=reason or f"Project transitioned from {previous_phase} to {new_phase}",
            previous_state={"phase": previous_phase},
            new_state={"phase": new_phase},
            event_data={"reason": reason},
            triggered_by=current_user.user_id
        )
        
        self.db.commit()
        self.db.refresh(project)
        
        logger.info(f"Project {project_id} transitioned from {previous_phase} to {new_phase}")
        return project
    
    def archive_project(
        self,
        project_id: uuid.UUID,
        current_user: User,
        reason: Optional[str] = None
    ) -> ProjectExtended:
        """Archive project"""
        return self.transition_project_phase(
            project_id=project_id,
            new_phase=ProjectPhase.ARCHIVED,
            current_user=current_user,
            reason=reason or "Project archived"
        )
    
    def _is_valid_phase_transition(
        self, 
        current_phase: ProjectPhase, 
        new_phase: ProjectPhase
    ) -> bool:
        """Validate if phase transition is allowed"""
        
        # Define valid transitions
        valid_transitions = {
            ProjectPhase.SETUP: [ProjectPhase.PLANNING, ProjectPhase.ARCHIVED],
            ProjectPhase.PLANNING: [ProjectPhase.ACTIVE, ProjectPhase.SETUP, ProjectPhase.ARCHIVED],
            ProjectPhase.ACTIVE: [ProjectPhase.PAUSED, ProjectPhase.COMPLETED, ProjectPhase.ARCHIVED],
            ProjectPhase.PAUSED: [ProjectPhase.ACTIVE, ProjectPhase.ARCHIVED],
            ProjectPhase.COMPLETED: [ProjectPhase.ARCHIVED],
            ProjectPhase.ARCHIVED: []  # No transitions from archived
        }
        
        return new_phase in valid_transitions.get(current_phase, [])
    
    def _create_lifecycle_event(
        self,
        project_id: uuid.UUID,
        event_type: str,
        event_name: str,
        description: Optional[str] = None,
        previous_state: Optional[Dict] = None,
        new_state: Optional[Dict] = None,
        event_data: Optional[Dict] = None,
        triggered_by: Optional[uuid.UUID] = None,
        trigger_type: str = "manual"
    ) -> ProjectLifecycleEvent:
        """Create lifecycle event"""
        
        event = ProjectLifecycleEvent(
            project_id=project_id,
            event_type=event_type,
            event_name=event_name,
            description=description,
            previous_state=previous_state or {},
            new_state=new_state or {},
            event_data=event_data or {},
            triggered_by=triggered_by,
            trigger_type=trigger_type
        )
        
        self.db.add(event)
        return event
    
    def _setup_default_roles(
        self,
        project: ProjectExtended,
        template: ProjectTemplate,
        creator: User
    ) -> None:
        """Setup default roles for project from template"""
        
        # Create project owner membership
        owner_membership = ProjectMembership(
            project_id=project.project_id,
            user_id=creator.user_id,
            role_name="project_owner",
            permissions=template.default_permissions.get("project_owner", {}),
            assigned_by=creator.user_id
        )
        
        self.db.add(owner_membership)

class ProjectMetricsService:
    """Service for managing project metrics and KPIs"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_metric(
        self,
        project_id: uuid.UUID,
        metric_data: ProjectMetricCreate,
        current_user: User
    ) -> ProjectMetric:
        """Create project metric"""
        
        # Check if metric already exists
        existing = self.db.query(ProjectMetric).filter(
            and_(
                ProjectMetric.project_id == project_id,
                ProjectMetric.metric_name == metric_data.metric_name
            )
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Metric with this name already exists for the project"
            )
        
        db_metric = ProjectMetric(
            project_id=project_id,
            **metric_data.dict()
        )
        
        self.db.add(db_metric)
        self.db.commit()
        self.db.refresh(db_metric)
        
        logger.info(f"Metric created: {db_metric.metric_id} for project {project_id}")
        return db_metric
    
    def update_metric_value(
        self,
        metric_id: uuid.UUID,
        new_value: float,
        current_user: User
    ) -> Optional[ProjectMetric]:
        """Update metric value"""
        
        metric = self.db.query(ProjectMetric).filter(
            ProjectMetric.metric_id == metric_id
        ).first()
        
        if not metric:
            return None
        
        metric.update_value(new_value, self.db)
        
        logger.info(f"Metric updated: {metric_id} new value: {new_value}")
        return metric
    
    def get_project_metrics(
        self,
        project_id: uuid.UUID,
        metric_type: Optional[MetricType] = None
    ) -> List[ProjectMetric]:
        """Get project metrics"""
        
        query = self.db.query(ProjectMetric).filter(
            ProjectMetric.project_id == project_id
        )
        
        if metric_type:
            query = query.filter(ProjectMetric.metric_type == metric_type)
        
        return query.order_by(ProjectMetric.metric_name).all()
    
    def calculate_project_health(
        self,
        project_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Calculate overall project health score"""
        
        metrics = self.get_project_metrics(project_id)
        
        if not metrics:
            return {"health_score": 100, "status": "healthy", "details": []}
        
        health_factors = []
        critical_count = 0
        warning_count = 0
        
        for metric in metrics:
            factor = {
                "metric_name": metric.metric_name,
                "status": metric.status,
                "current_value": float(metric.current_value),
                "target_value": float(metric.target_value) if metric.target_value else None,
                "percentage_of_target": metric.percentage_of_target
            }
            
            if metric.status == MetricStatus.CRITICAL:
                critical_count += 1
                factor["impact"] = -20
            elif metric.status == MetricStatus.WARNING:
                warning_count += 1
                factor["impact"] = -10
            else:
                factor["impact"] = 0
            
            health_factors.append(factor)
        
        # Calculate overall health score
        base_score = 100
        health_score = max(0, base_score - (critical_count * 20) - (warning_count * 10))
        
        # Determine status
        if critical_count > 0:
            status = "critical"
        elif warning_count > 0:
            status = "warning"
        else:
            status = "healthy"
        
        return {
            "health_score": health_score,
            "status": status,
            "critical_metrics": critical_count,
            "warning_metrics": warning_count,
            "total_metrics": len(metrics),
            "details": health_factors
        }

class ProjectAnalyticsService:
    """Service for project analytics and insights"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_organization_stats(
        self,
        org_id: uuid.UUID
    ) -> ProjectStats:
        """Get organization project statistics"""
        
        # Get all projects for organization
        projects_query = self.db.query(ProjectExtended).filter(
            ProjectExtended.org_id == org_id
        )
        
        total_projects = projects_query.count()
        active_projects = projects_query.filter(
            ProjectExtended.project_phase == ProjectPhase.ACTIVE
        ).count()
        completed_projects = projects_query.filter(
            ProjectExtended.project_phase == ProjectPhase.COMPLETED
        ).count()
        
        # Calculate averages
        avg_health = projects_query.with_entities(
            func.avg(ProjectExtended.health_score)
        ).scalar() or 0.0
        
        avg_completion = projects_query.with_entities(
            func.avg(ProjectExtended.completion_percentage)
        ).scalar() or 0.0
        
        return ProjectStats(
            total_projects=total_projects,
            active_projects=active_projects,
            completed_projects=completed_projects,
            avg_health_score=float(avg_health),
            avg_completion=float(avg_completion)
        )
    
    def get_project_performance_history(
        self,
        project_id: uuid.UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        snapshot_type: str = "daily"
    ) -> List[ProjectPerformanceSnapshot]:
        """Get project performance history"""
        
        query = self.db.query(ProjectPerformanceSnapshot).filter(
            ProjectPerformanceSnapshot.project_id == project_id,
            ProjectPerformanceSnapshot.snapshot_type == snapshot_type
        )
        
        if start_date:
            query = query.filter(ProjectPerformanceSnapshot.snapshot_date >= start_date)
        if end_date:
            query = query.filter(ProjectPerformanceSnapshot.snapshot_date <= end_date)
        
        return query.order_by(ProjectPerformanceSnapshot.snapshot_date).all()
    
    def create_performance_snapshot(
        self,
        project_id: uuid.UUID,
        snapshot_date: date,
        metrics_data: Dict[str, Any]
    ) -> ProjectPerformanceSnapshot:
        """Create performance snapshot"""
        
        snapshot = ProjectPerformanceSnapshot(
            project_id=project_id,
            snapshot_date=snapshot_date,
            **metrics_data
        )
        
        self.db.add(snapshot)
        self.db.commit()
        self.db.refresh(snapshot)
        
        return snapshot

class ProjectManagementService:
    """Main project management service orchestrator"""
    
    def __init__(self, db: Session):
        self.db = db
        self.template_service = ProjectTemplateService(db)
        self.lifecycle_service = ProjectLifecycleService(db)
        self.metrics_service = ProjectMetricsService(db)
        self.analytics_service = ProjectAnalyticsService(db)
    
    def get_user_projects(
        self,
        user_id: uuid.UUID,
        org_id: Optional[uuid.UUID] = None,
        phase_filter: Optional[List[ProjectPhase]] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[ProjectExtended]:
        """Get projects accessible to user"""
        
        # Query projects through memberships
        query = self.db.query(ProjectExtended).join(
            ProjectMembership,
            ProjectExtended.project_id == ProjectMembership.project_id
        ).filter(
            ProjectMembership.user_id == user_id,
            ProjectMembership.is_active == True
        )
        
        if org_id:
            query = query.filter(ProjectExtended.org_id == org_id)
        
        if phase_filter:
            query = query.filter(ProjectExtended.project_phase.in_(phase_filter))
        
        # Order by last activity
        query = query.order_by(desc(ProjectExtended.last_activity_at))
        
        return query.offset(skip).limit(limit).all()
    
    def get_project_dashboard(
        self,
        project_id: uuid.UUID,
        current_user: User
    ) -> Dict[str, Any]:
        """Get comprehensive project dashboard data"""
        
        # Get project
        project = self.db.query(ProjectExtended).filter(
            ProjectExtended.project_id == project_id
        ).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Get project health
        health_data = self.metrics_service.calculate_project_health(project_id)
        
        # Get recent activity
        recent_events = self.db.query(ProjectLifecycleEvent).filter(
            ProjectLifecycleEvent.project_id == project_id
        ).order_by(desc(ProjectLifecycleEvent.occurred_at)).limit(10).all()
        
        # Get team members
        team_members = self.db.query(ProjectMembership).join(User).filter(
            ProjectMembership.project_id == project_id,
            ProjectMembership.is_active == True
        ).all()
        
        # Get performance trend (last 30 days)
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        performance_history = self.analytics_service.get_project_performance_history(
            project_id, start_date, end_date
        )
        
        return {
            "project": project,
            "health": health_data,
            "recent_activity": recent_events,
            "team_members": team_members,
            "performance_trend": performance_history,
            "metrics_summary": {
                "total_conversations": sum(p.total_conversations for p in performance_history),
                "active_users": performance_history[-1].active_users if performance_history else 0,
                "avg_satisfaction": sum(p.user_satisfaction_score for p in performance_history) / len(performance_history) if performance_history else 0,
                "uptime_avg": sum(p.uptime_percentage for p in performance_history) / len(performance_history) if performance_history else 100
            }
        }
```

---

## 🔌 **FastAPI Router Implementation**

### **📍 Project Management API Endpoints:**

```python
# routers/projects.py - Project Management API Router
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import uuid
from datetime import date

from ..database import get_db
from ..core.security import get_current_user, require_permission
from ..models.user import User
from ..services.project_management import (
    ProjectManagementService, ProjectTemplateService,
    ProjectLifecycleService, ProjectMetricsService
)
from ..schemas.project import (
    ProjectTemplateResponse, ProjectTemplateCreate, ProjectTemplateUpdate,
    ProjectResponse, ProjectCreate, ProjectUpdate,
    ProjectMetricResponse, ProjectMetricCreate, ProjectMetricUpdate,
    ProjectDashboardResponse, ProjectStatsResponse
)

router = APIRouter(
    prefix="/api/v1/projects",
    tags=["Project Management"],
    dependencies=[Depends(get_current_user)]
)

# Project Templates Endpoints
@router.get("/templates", response_model=List[ProjectTemplateResponse])
async def get_project_templates(
    category: Optional[str] = Query(None, description="Filter by category"),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    complexity: Optional[str] = Query(None, description="Filter by setup complexity"),
    is_featured: Optional[bool] = Query(None, description="Filter featured templates"),
    skip: int = Query(0, ge=0, description="Number of templates to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of templates to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get available project templates"""
    
    template_service = ProjectTemplateService(db)
    templates = template_service.get_templates(
        category=category,
        industry=industry,
        complexity=complexity,
        is_featured=is_featured,
        skip=skip,
        limit=limit
    )
    
    return templates

@router.get("/templates/{template_id}", response_model=ProjectTemplateResponse)
async def get_project_template(
    template_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific project template"""
    
    template_service = ProjectTemplateService(db)
    template = template_service.get_template(template_id)
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    return template

@router.post("/templates", response_model=ProjectTemplateResponse)
async def create_project_template(
    template_data: ProjectTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("create_templates"))
):
    """Create new project template"""
    
    template_service = ProjectTemplateService(db)
    return template_service.create_template(template_data, current_user)

# Project Management Endpoints
@router.get("/", response_model=List[ProjectResponse])
async def get_user_projects(
    org_id: Optional[uuid.UUID] = Query(None, description="Filter by organization"),
    phase: Optional[List[str]] = Query(None, description="Filter by project phase"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get projects accessible to current user"""
    
    project_service = ProjectManagementService(db)
    return project_service.get_user_projects(
        user_id=current_user.user_id,
        org_id=org_id,
        phase_filter=phase,
        skip=skip,
        limit=limit
    )

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_project"))
):
    """Get specific project details"""
    
    project = db.query(ProjectExtended).filter(
        ProjectExtended.project_id == project_id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return project

@router.post("/from-template/{template_id}", response_model=ProjectResponse)
async def create_project_from_template(
    template_id: uuid.UUID,
    project_data: ProjectCreate,
    org_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("create_project"))
):
    """Create project from template"""
    
    project_service = ProjectManagementService(db)
    return project_service.lifecycle_service.create_project_from_template(
        template_id=template_id,
        project_data=project_data,
        org_id=org_id,
        current_user=current_user
    )

@router.put("/{project_id}/phase", response_model=ProjectResponse)
async def update_project_phase(
    project_id: uuid.UUID,
    new_phase: str,
    reason: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_project"))
):
    """Update project phase"""
    
    project_service = ProjectManagementService(db)
    return project_service.lifecycle_service.transition_project_phase(
        project_id=project_id,
        new_phase=new_phase,
        current_user=current_user,
        reason=reason
    )

@router.post("/{project_id}/archive", response_model=ProjectResponse)
async def archive_project(
    project_id: uuid.UUID,
    reason: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("archive_project"))
):
    """Archive project"""
    
    project_service = ProjectManagementService(db)
    return project_service.lifecycle_service.archive_project(
        project_id=project_id,
        current_user=current_user,
        reason=reason
    )

@router.get("/{project_id}/dashboard", response_model=ProjectDashboardResponse)
async def get_project_dashboard(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_project"))
):
    """Get comprehensive project dashboard"""
    
    project_service = ProjectManagementService(db)
    return project_service.get_project_dashboard(project_id, current_user)

# Project Metrics Endpoints
@router.get("/{project_id}/metrics", response_model=List[ProjectMetricResponse])
async def get_project_metrics(
    project_id: uuid.UUID,
    metric_type: Optional[str] = Query(None, description="Filter by metric type"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_project"))
):
    """Get project metrics"""
    
    metrics_service = ProjectMetricsService(db)
    return metrics_service.get_project_metrics(project_id, metric_type)

@router.post("/{project_id}/metrics", response_model=ProjectMetricResponse)
async def create_project_metric(
    project_id: uuid.UUID,
    metric_data: ProjectMetricCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_project"))
):
    """Create project metric"""
    
    metrics_service = ProjectMetricsService(db)
    return metrics_service.create_metric(project_id, metric_data, current_user)

@router.put("/metrics/{metric_id}/value")
async def update_metric_value(
    metric_id: uuid.UUID,
    new_value: float,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_project"))
):
    """Update metric value"""
    
    metrics_service = ProjectMetricsService(db)
    metric = metrics_service.update_metric_value(metric_id, new_value, current_user)
    
    if not metric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Metric not found"
        )
    
    return {"message": "Metric updated successfully"}

@router.get("/{project_id}/health")
async def get_project_health(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_project"))
):
    """Get project health score and status"""
    
    metrics_service = ProjectMetricsService(db)
    return metrics_service.calculate_project_health(project_id)

# Analytics Endpoints
@router.get("/analytics/organization/{org_id}/stats", response_model=ProjectStatsResponse)
async def get_organization_project_stats(
    org_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_organization"))
):
    """Get organization project statistics"""
    
    project_service = ProjectManagementService(db)
    return project_service.analytics_service.get_organization_stats(org_id)

@router.get("/{project_id}/performance/history")
async def get_project_performance_history(
    project_id: uuid.UUID,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    snapshot_type: str = Query("daily", description="daily, weekly, monthly"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_project"))
):
    """Get project performance history"""
    
    project_service = ProjectManagementService(db)
    return project_service.analytics_service.get_project_performance_history(
        project_id, start_date, end_date, snapshot_type
    )
```

พร้อม**สร้าง Pydantic Schemas และ Frontend Interface** ต่อไหมครับ? 🎨

หรือต้องการให้ผมปรับแต่งส่วนไหนก่อนครับ? 🔧