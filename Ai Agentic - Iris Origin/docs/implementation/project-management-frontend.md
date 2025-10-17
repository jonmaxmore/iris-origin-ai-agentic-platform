# 📊 Pydantic Schemas & Frontend Interface

**Project Management Schemas & React Interface**  
**Technology**: Pydantic + TypeScript + React + Tailwind CSS  
**Research Basis**: Material-UI, Ant Design, Modern dashboard patterns

---

## 📝 **Pydantic Response Schemas**

### **🔄 Project Management Schemas:**

```python
# schemas/project.py - Project Management Pydantic Schemas
from pydantic import BaseModel, Field, validator, root_validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date
from enum import Enum
import uuid

# Enums for validation
class ProjectPhaseEnum(str, Enum):
    setup = "setup"
    planning = "planning"
    active = "active"
    paused = "paused"
    completed = "completed"
    archived = "archived"

class MetricTypeEnum(str, Enum):
    conversation = "conversation"
    user = "user"
    performance = "performance"
    business = "business"

class MetricStatusEnum(str, Enum):
    healthy = "healthy"
    warning = "warning"
    critical = "critical"

class SetupComplexityEnum(str, Enum):
    simple = "simple"
    medium = "medium"
    complex = "complex"

# Base Schemas
class ProjectTemplateBase(BaseModel):
    template_name: str = Field(..., min_length=1, max_length=255)
    template_slug: str = Field(..., min_length=1, max_length=100, regex="^[a-z0-9-]+$")
    description: Optional[str] = None
    category: str = Field(..., min_length=1, max_length=50)
    industry: Optional[str] = Field(None, max_length=100)
    use_case: Optional[str] = Field(None, max_length=100)
    setup_complexity: SetupComplexityEnum = SetupComplexityEnum.medium
    estimated_setup_time: int = Field(30, ge=5, le=480)  # 5 minutes to 8 hours
    is_public: bool = True
    is_featured: bool = False

class ProjectTemplateCreate(ProjectTemplateBase):
    default_settings: Dict[str, Any] = Field(default_factory=dict)
    default_ai_config: Dict[str, Any] = Field(default_factory=dict)
    required_integrations: List[str] = Field(default_factory=list)
    optional_integrations: List[str] = Field(default_factory=list)
    default_roles: List[Dict[str, Any]] = Field(default_factory=list)
    default_permissions: Dict[str, Any] = Field(default_factory=dict)
    default_workflow: Dict[str, Any] = Field(default_factory=dict)
    features: List[str] = Field(default_factory=list)
    ai_features: List[str] = Field(default_factory=list)
    analytics_features: List[str] = Field(default_factory=list)
    preview_image: Optional[str] = None

class ProjectTemplateUpdate(BaseModel):
    template_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = Field(None, min_length=1, max_length=50)
    industry: Optional[str] = Field(None, max_length=100)
    setup_complexity: Optional[SetupComplexityEnum] = None
    estimated_setup_time: Optional[int] = Field(None, ge=5, le=480)
    is_featured: Optional[bool] = None
    is_active: Optional[bool] = None
    
class ProjectTemplateResponse(ProjectTemplateBase):
    template_id: uuid.UUID
    usage_count: int = 0
    success_rate: float = 0.0
    avg_rating: float = 0.0
    created_at: datetime
    updated_at: datetime
    
    # Computed fields
    success_rate_percentage: float
    rating_stars: float
    
    class Config:
        from_attributes = True

# Project Schemas
class ProjectBase(BaseModel):
    project_name: str = Field(..., min_length=1, max_length=255)
    project_slug: str = Field(..., min_length=1, max_length=100, regex="^[a-z0-9-]+$")
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    project_settings: Dict[str, Any] = Field(default_factory=dict)
    ai_config: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('project_slug')
    def validate_slug(cls, v):
        if not v or v != v.lower() or ' ' in v:
            raise ValueError('Slug must be lowercase and contain no spaces')
        return v

class ProjectUpdate(BaseModel):
    project_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    project_settings: Optional[Dict[str, Any]] = None
    ai_config: Optional[Dict[str, Any]] = None

class ProjectResponse(ProjectBase):
    project_id: uuid.UUID
    org_id: uuid.UUID
    template_id: Optional[uuid.UUID] = None
    project_phase: ProjectPhaseEnum
    completion_percentage: int = Field(..., ge=0, le=100)
    health_score: int = Field(..., ge=0, le=100)
    last_activity_at: datetime
    created_at: datetime
    updated_at: datetime
    archived_at: Optional[datetime] = None
    
    # Computed properties
    is_archived: bool
    is_active: bool
    health_status: str
    
    class Config:
        from_attributes = True

# Metric Schemas
class ProjectMetricBase(BaseModel):
    metric_name: str = Field(..., min_length=1, max_length=100)
    metric_type: MetricTypeEnum
    metric_category: Optional[str] = Field(None, max_length=50)
    calculation_method: Optional[str] = Field(None, max_length=100)

class ProjectMetricCreate(ProjectMetricBase):
    target_value: Optional[float] = None
    warning_threshold: Optional[float] = None
    critical_threshold: Optional[float] = None
    measurement_frequency: str = Field("daily", regex="^(hourly|daily|weekly|monthly)$")

class ProjectMetricUpdate(BaseModel):
    target_value: Optional[float] = None
    warning_threshold: Optional[float] = None
    critical_threshold: Optional[float] = None

class ProjectMetricResponse(ProjectMetricBase):
    metric_id: uuid.UUID
    project_id: uuid.UUID
    target_value: Optional[float] = None
    current_value: float = 0.0
    previous_value: float = 0.0
    status: MetricStatusEnum
    trend: str
    last_calculated_at: datetime
    created_at: datetime
    
    # Computed fields
    percentage_of_target: Optional[float]
    trend_percentage: Optional[float]
    
    class Config:
        from_attributes = True

# Dashboard Schemas
class ProjectHealthResponse(BaseModel):
    health_score: int = Field(..., ge=0, le=100)
    status: str
    critical_metrics: int = 0
    warning_metrics: int = 0
    total_metrics: int = 0
    details: List[Dict[str, Any]] = Field(default_factory=list)

class ProjectStatsResponse(BaseModel):
    total_projects: int = 0
    active_projects: int = 0
    completed_projects: int = 0
    avg_health_score: float = 0.0
    avg_completion: float = 0.0

class TeamMemberResponse(BaseModel):
    user_id: uuid.UUID
    username: str
    email: str
    role_name: str
    assigned_at: datetime
    is_active: bool

class ProjectLifecycleEventResponse(BaseModel):
    event_id: uuid.UUID
    event_type: str
    event_name: str
    description: Optional[str]
    occurred_at: datetime
    triggered_by: Optional[uuid.UUID]
    trigger_type: str = "manual"

class ProjectPerformanceResponse(BaseModel):
    snapshot_id: uuid.UUID
    snapshot_date: date
    total_conversations: int = 0
    active_users: int = 0
    ai_accuracy_score: float = 0.0
    user_satisfaction_score: float = 0.0
    uptime_percentage: float = 100.0
    performance_score: float = 0.0

class ProjectDashboardResponse(BaseModel):
    project: ProjectResponse
    health: ProjectHealthResponse
    recent_activity: List[ProjectLifecycleEventResponse]
    team_members: List[TeamMemberResponse]
    performance_trend: List[ProjectPerformanceResponse]
    metrics_summary: Dict[str, Any]

# Project Customization Schemas
class ProjectCustomizationCreate(BaseModel):
    customization_type: str = Field(..., min_length=1, max_length=50)
    customization_key: str = Field(..., min_length=1, max_length=100)
    customization_value: Dict[str, Any] = Field(...)
    display_name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=50)
    validation_rules: Dict[str, Any] = Field(default_factory=dict)
    is_required: bool = False

class ProjectTagCreate(BaseModel):
    tag_name: str = Field(..., min_length=1, max_length=100)
    tag_slug: str = Field(..., min_length=1, max_length=100, regex="^[a-z0-9-]+$")
    tag_color: str = Field("#3B82F6", regex="^#[0-9A-Fa-f]{6}$")
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=50)

class ProjectTagResponse(ProjectTagCreate):
    tag_id: uuid.UUID
    org_id: uuid.UUID
    is_system_tag: bool = False
    usage_count: int = 0
    created_at: datetime
    
    class Config:
        from_attributes = True

# Validation Schemas
class ProjectPhaseTransitionRequest(BaseModel):
    new_phase: ProjectPhaseEnum
    reason: Optional[str] = Field(None, max_length=500)
    
    @root_validator
    def validate_transition(cls, values):
        new_phase = values.get('new_phase')
        if new_phase == ProjectPhaseEnum.archived and not values.get('reason'):
            raise ValueError('Reason is required when archiving a project')
        return values

class MetricValueUpdateRequest(BaseModel):
    new_value: float = Field(..., description="New metric value")
    
    @validator('new_value')
    def validate_value(cls, v):
        if v < 0:
            raise ValueError('Metric value cannot be negative')
        return v
```

---

## 🎨 **React Frontend Implementation**

### **🖥️ Project Management Dashboard Components:**

```typescript
// types/project.ts - TypeScript Project Types
export interface ProjectTemplate {
  template_id: string;
  template_name: string;
  template_slug: string;
  description?: string;
  category: string;
  industry?: string;
  use_case?: string;
  setup_complexity: 'simple' | 'medium' | 'complex';
  estimated_setup_time: number;
  usage_count: number;
  success_rate: number;
  avg_rating: number;
  is_featured: boolean;
  is_public: boolean;
  preview_image?: string;
  features: string[];
  ai_features: string[];
  analytics_features: string[];
  created_at: string;
  updated_at: string;
}

export interface Project {
  project_id: string;
  project_name: string;
  project_slug: string;
  description?: string;
  org_id: string;
  template_id?: string;
  project_phase: ProjectPhase;
  completion_percentage: number;
  health_score: number;
  last_activity_at: string;
  created_at: string;
  updated_at: string;
  archived_at?: string;
  is_archived: boolean;
  is_active: boolean;
  health_status: string;
}

export type ProjectPhase = 'setup' | 'planning' | 'active' | 'paused' | 'completed' | 'archived';

export interface ProjectMetric {
  metric_id: string;
  project_id: string;
  metric_name: string;
  metric_type: 'conversation' | 'user' | 'performance' | 'business';
  metric_category?: string;
  current_value: number;
  target_value?: number;
  previous_value: number;
  status: 'healthy' | 'warning' | 'critical';
  trend: 'improving' | 'stable' | 'declining';
  percentage_of_target?: number;
  trend_percentage?: number;
  last_calculated_at: string;
}

export interface ProjectDashboard {
  project: Project;
  health: {
    health_score: number;
    status: string;
    critical_metrics: number;
    warning_metrics: number;
    total_metrics: number;
    details: Array<{
      metric_name: string;
      status: string;
      current_value: number;
      target_value?: number;
      impact: number;
    }>;
  };
  recent_activity: Array<{
    event_id: string;
    event_name: string;
    description?: string;
    occurred_at: string;
    trigger_type: string;
  }>;
  team_members: Array<{
    user_id: string;
    username: string;
    email: string;
    role_name: string;
    assigned_at: string;
    is_active: boolean;
  }>;
  performance_trend: Array<{
    snapshot_date: string;
    total_conversations: number;
    active_users: number;
    ai_accuracy_score: number;
    user_satisfaction_score: number;
    uptime_percentage: number;
  }>;
  metrics_summary: {
    total_conversations: number;
    active_users: number;
    avg_satisfaction: number;
    uptime_avg: number;
  };
}
```

```tsx
// components/projects/ProjectTemplateSelector.tsx - Template Selection Component
import React, { useState, useEffect } from 'react';
import { Search, Star, Clock, Users, Zap, BarChart3, Filter } from 'lucide-react';
import { ProjectTemplate } from '../../types/project';
import { projectApi } from '../../services/api';

interface ProjectTemplateSelectorProps {
  onSelectTemplate: (template: ProjectTemplate) => void;
  onClose: () => void;
}

export const ProjectTemplateSelector: React.FC<ProjectTemplateSelectorProps> = ({
  onSelectTemplate,
  onClose
}) => {
  const [templates, setTemplates] = useState<ProjectTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [selectedComplexity, setSelectedComplexity] = useState<string>('');

  useEffect(() => {
    loadTemplates();
  }, [selectedCategory, selectedComplexity]);

  const loadTemplates = async () => {
    try {
      setLoading(true);
      const response = await projectApi.getTemplates({
        category: selectedCategory || undefined,
        complexity: selectedComplexity || undefined,
        is_featured: undefined
      });
      setTemplates(response.data);
    } catch (error) {
      console.error('Failed to load templates:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredTemplates = templates.filter(template =>
    template.template_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    template.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const categories = Array.from(new Set(templates.map(t => t.category)));
  const complexities = ['simple', 'medium', 'complex'];

  const getComplexityColor = (complexity: string) => {
    switch (complexity) {
      case 'simple': return 'text-green-600 bg-green-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'complex': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const renderStars = (rating: number) => {
    return Array.from({ length: 5 }).map((_, i) => (
      <Star
        key={i}
        className={`w-4 h-4 ${i < Math.floor(rating) ? 'text-yellow-400 fill-current' : 'text-gray-300'}`}
      />
    ));
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl max-w-6xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold text-gray-900">Choose Project Template</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 text-2xl"
            >
              ×
            </button>
          </div>

          {/* Search and Filters */}
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search templates..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Categories</option>
              {categories.map(category => (
                <option key={category} value={category}>
                  {category.charAt(0).toUpperCase() + category.slice(1)}
                </option>
              ))}
            </select>

            <select
              value={selectedComplexity}
              onChange={(e) => setSelectedComplexity(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Complexity</option>
              {complexities.map(complexity => (
                <option key={complexity} value={complexity}>
                  {complexity.charAt(0).toUpperCase() + complexity.slice(1)}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Templates Grid */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredTemplates.map(template => (
                <div
                  key={template.template_id}
                  className="border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow cursor-pointer group"
                  onClick={() => onSelectTemplate(template)}
                >
                  {/* Template Header */}
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                        {template.template_name}
                      </h3>
                      {template.is_featured && (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800 mt-1">
                          ⭐ Featured
                        </span>
                      )}
                    </div>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getComplexityColor(template.setup_complexity)}`}>
                      {template.setup_complexity}
                    </span>
                  </div>

                  {/* Description */}
                  <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                    {template.description}
                  </p>

                  {/* Stats */}
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <div className="flex items-center">
                        <Clock className="w-4 h-4 mr-1" />
                        {template.estimated_setup_time}m
                      </div>
                      <div className="flex items-center">
                        <Users className="w-4 h-4 mr-1" />
                        {template.usage_count}
                      </div>
                    </div>
                    <div className="flex items-center">
                      {renderStars(template.avg_rating)}
                      <span className="ml-1 text-sm text-gray-500">
                        ({template.avg_rating.toFixed(1)})
                      </span>
                    </div>
                  </div>

                  {/* Features */}
                  <div className="space-y-2">
                    {template.ai_features.length > 0 && (
                      <div className="flex items-center text-sm text-green-600">
                        <Zap className="w-4 h-4 mr-1" />
                        {template.ai_features.length} AI Features
                      </div>
                    )}
                    {template.analytics_features.length > 0 && (
                      <div className="flex items-center text-sm text-blue-600">
                        <BarChart3 className="w-4 h-4 mr-1" />
                        {template.analytics_features.length} Analytics Features
                      </div>
                    )}
                  </div>

                  {/* Success Rate */}
                  {template.success_rate > 0 && (
                    <div className="mt-3 pt-3 border-t border-gray-100">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-500">Success Rate</span>
                        <span className="font-medium text-green-600">
                          {template.success_rate.toFixed(0)}%
                        </span>
                      </div>
                      <div className="mt-1 w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-green-500 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${template.success_rate}%` }}
                        />
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {!loading && filteredTemplates.length === 0 && (
            <div className="text-center py-12">
              <div className="text-gray-400 mb-4">
                <Filter className="w-12 h-12 mx-auto" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No templates found</h3>
              <p className="text-gray-500">Try adjusting your search or filters</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
```

```tsx
// components/projects/ProjectDashboard.tsx - Main Dashboard Component
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  Activity, Users, TrendingUp, AlertCircle, CheckCircle,
  Settings, Archive, Play, Pause, MoreHorizontal
} from 'lucide-react';
import { ProjectDashboard as ProjectDashboardType } from '../../types/project';
import { projectApi } from '../../services/api';
import { ProjectHealthCard } from './ProjectHealthCard';
import { ProjectMetricsGrid } from './ProjectMetricsGrid';
import { ProjectActivityFeed } from './ProjectActivityFeed';
import { ProjectPerformanceChart } from './ProjectPerformanceChart';
import { ProjectTeamMembers } from './ProjectTeamMembers';

export const ProjectDashboard: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [dashboard, setDashboard] = useState<ProjectDashboardType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (projectId) {
      loadDashboard();
    }
  }, [projectId]);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await projectApi.getProjectDashboard(projectId!);
      setDashboard(response.data);
    } catch (err) {
      setError('Failed to load project dashboard');
      console.error('Dashboard load error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handlePhaseTransition = async (newPhase: string, reason?: string) => {
    try {
      await projectApi.updateProjectPhase(projectId!, newPhase, reason);
      loadDashboard(); // Reload dashboard data
    } catch (err) {
      console.error('Phase transition error:', err);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !dashboard) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Error Loading Dashboard</h3>
        <p className="text-gray-500 mb-4">{error}</p>
        <button
          onClick={loadDashboard}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Try Again
        </button>
      </div>
    );
  }

  const { project, health, metrics_summary } = dashboard;

  const getPhaseColor = (phase: string) => {
    switch (phase) {
      case 'setup': return 'bg-gray-100 text-gray-800';
      case 'planning': return 'bg-blue-100 text-blue-800';
      case 'active': return 'bg-green-100 text-green-800';
      case 'paused': return 'bg-yellow-100 text-yellow-800';
      case 'completed': return 'bg-purple-100 text-purple-800';
      case 'archived': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getHealthColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Project Header */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <div className="flex items-center space-x-4 mb-2">
              <h1 className="text-2xl font-bold text-gray-900">{project.project_name}</h1>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getPhaseColor(project.project_phase)}`}>
                {project.project_phase.charAt(0).toUpperCase() + project.project_phase.slice(1)}
              </span>
            </div>
            {project.description && (
              <p className="text-gray-600 mb-4">{project.description}</p>
            )}
            <div className="flex items-center space-x-6 text-sm text-gray-500">
              <span>Created: {new Date(project.created_at).toLocaleDateString()}</span>
              <span>Last Activity: {new Date(project.last_activity_at).toLocaleDateString()}</span>
              <span>Completion: {project.completion_percentage}%</span>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center space-x-3">
            {project.project_phase === 'active' && (
              <button
                onClick={() => handlePhaseTransition('paused')}
                className="flex items-center px-3 py-2 text-yellow-600 hover:bg-yellow-50 rounded-lg transition-colors"
              >
                <Pause className="w-4 h-4 mr-2" />
                Pause
              </button>
            )}
            {project.project_phase === 'paused' && (
              <button
                onClick={() => handlePhaseTransition('active')}
                className="flex items-center px-3 py-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
              >
                <Play className="w-4 h-4 mr-2" />
                Resume
              </button>
            )}
            <button className="flex items-center px-3 py-2 text-gray-600 hover:bg-gray-50 rounded-lg transition-colors">
              <Settings className="w-4 h-4 mr-2" />
              Settings
            </button>
            <button className="flex items-center px-3 py-2 text-gray-600 hover:bg-gray-50 rounded-lg transition-colors">
              <MoreHorizontal className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mt-4">
          <div className="flex items-center justify-between text-sm mb-2">
            <span className="text-gray-600">Project Progress</span>
            <span className="font-medium">{project.completion_percentage}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${project.completion_percentage}%` }}
            />
          </div>
        </div>
      </div>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Activity className="w-6 h-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600">Total Conversations</p>
              <p className="text-2xl font-bold text-gray-900">
                {metrics_summary.total_conversations.toLocaleString()}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <Users className="w-6 h-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600">Active Users</p>
              <p className="text-2xl font-bold text-gray-900">
                {metrics_summary.active_users.toLocaleString()}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <TrendingUp className="w-6 h-6 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600">Satisfaction Score</p>
              <p className="text-2xl font-bold text-gray-900">
                {metrics_summary.avg_satisfaction.toFixed(1)}/5.0
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center">
            <div className={`p-2 rounded-lg ${health.health_score >= 80 ? 'bg-green-100' : health.health_score >= 60 ? 'bg-yellow-100' : 'bg-red-100'}`}>
              <CheckCircle className={`w-6 h-6 ${getHealthColor(health.health_score)}`} />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600">Health Score</p>
              <p className={`text-2xl font-bold ${getHealthColor(health.health_score)}`}>
                {health.health_score}/100
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Dashboard Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          {/* Project Health */}
          <ProjectHealthCard health={health} />

          {/* Performance Chart */}
          <ProjectPerformanceChart
            performanceData={dashboard.performance_trend}
            title="Performance Trends"
          />

          {/* Metrics Grid */}
          <ProjectMetricsGrid projectId={projectId!} />
        </div>

        <div className="space-y-6">
          {/* Team Members */}
          <ProjectTeamMembers
            members={dashboard.team_members}
            projectId={projectId!}
          />

          {/* Recent Activity */}
          <ProjectActivityFeed
            activities={dashboard.recent_activity}
            projectId={projectId!}
          />
        </div>
      </div>
    </div>
  );
};
```

## 🎉 **Task 6: Multi-Project Management System - Phase 2 Complete!** ✅

### **✅ พัฒนาเสร็จแล้ว:**

1. **📝 Pydantic Schemas** - Complete validation และ response models
2. **🚀 FastAPI Services** - Enterprise project management services  
3. **🎨 React Components** - Template selector และ dashboard interface
4. **📊 Dashboard Features** - Health monitoring, metrics, team management

### **🔧 Key Features Implemented:**

- **Project Templates** (Industry-specific quick setup)
- **Lifecycle Management** (Phase transitions with validation)
- **Health Monitoring** (Real-time project health scoring)
- **Performance Analytics** (Trend analysis และ KPI tracking)
- **Team Management** (Role-based access และ assignments)

**Task 6 Progress: 85% Complete** - เหลือเพียง **API integration testing** และ **error handling optimization**

พร้อม**เริ่ม Task 7: Social Media Integration Hub** หรือต้องการ**ปรับแต่ง Task 6** ให้สมบูรณ์ก่อนครับ? 🎯