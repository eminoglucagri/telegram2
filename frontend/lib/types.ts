// Campaign Types
export type CampaignStatus = 'active' | 'paused' | 'completed' | 'draft';

export interface Campaign {
  id: string;
  name: string;
  persona_id: string;
  status: CampaignStatus;
  start_date: string;
  end_date?: string;
  target_keywords: string[];
  description?: string;
  created_at: string;
  updated_at?: string;
}

export interface CampaignCreate {
  name: string;
  persona_id: string;
  target_keywords: string[];
  start_date: string;
  end_date?: string;
  description?: string;
}

export interface CampaignUpdate {
  name?: string;
  persona_id?: string;
  status?: CampaignStatus;
  target_keywords?: string[];
  end_date?: string;
  description?: string;
}

// Group Types
export type GroupStatus = 'active' | 'left' | 'banned' | 'pending';

export interface Group {
  id: string;
  telegram_id: number;
  title: string;
  username?: string;
  member_count: number;
  joined_at: string;
  status: GroupStatus;
  campaign_id?: string;
  description?: string;
}

export interface GroupCreate {
  username?: string;
  invite_link?: string;
  campaign_id?: string;
}

export interface GroupUpdate {
  status?: GroupStatus;
  campaign_id?: string;
}

// Message Types
export type SentimentType = 'positive' | 'negative' | 'neutral';
export type IntentType = 'question' | 'statement' | 'request' | 'complaint' | 'other';

export interface Message {
  id: string;
  telegram_id: number;
  group_id: string;
  sender_id: number;
  sender_username?: string;
  content: string;
  is_bot_message: boolean;
  is_dm: boolean;
  sentiment?: SentimentType;
  intent?: IntentType;
  created_at: string;
  campaign_id?: string;
}

export interface MessageStats {
  total_messages: number;
  bot_messages: number;
  user_messages: number;
  dm_count: number;
  sentiment_breakdown: Record<string, number>;
  daily_breakdown: Array<{ date: string; count: number }>;
}

// Lead Types
export type LeadStatus = 'new' | 'contacted' | 'engaged' | 'converted' | 'lost' | 'unqualified';

export interface Lead {
  id: string;
  telegram_id: number;
  username?: string;
  first_name?: string;
  last_name?: string;
  source_group_id: string;
  source_group_title?: string;
  campaign_id?: string;
  status: LeadStatus;
  score: number;
  contact_method?: string;
  notes?: string;
  contacted_at?: string;
  created_at: string;
  updated_at?: string;
}

export interface LeadCreate {
  telegram_id: number;
  username?: string;
  first_name?: string;
  source_group_id: string;
  campaign_id?: string;
  score?: number;
}

export interface LeadUpdate {
  status?: LeadStatus;
  score?: number;
  notes?: string;
  contact_method?: string;
}

// Persona Types
export interface Persona {
  id: string;
  name: string;
  bio: string;
  interests: string[];
  tone: string;
  language_style?: string;
  sample_messages: string[];
  keywords_to_engage: string[];
  keywords_to_avoid: string[];
  response_templates?: Record<string, string>;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface PersonaCreate {
  name: string;
  bio: string;
  interests: string[];
  tone: string;
  language_style?: string;
  sample_messages: string[];
  keywords_to_engage: string[];
  keywords_to_avoid: string[];
}

export interface PersonaUpdate {
  name?: string;
  bio?: string;
  interests?: string[];
  tone?: string;
  sample_messages?: string[];
  keywords_to_engage?: string[];
  keywords_to_avoid?: string[];
  is_active?: boolean;
}

// WarmUp Types
export type WarmUpStage = 'observer' | 'reactor' | 'participant' | 'contributor' | 'influencer';

export interface WarmUpMetric {
  id: string;
  user_id: string;
  date: string;
  stage: WarmUpStage;
  messages_sent: number;
  groups_joined: number;
  dms_sent: number;
  reactions_sent: number;
  health_score: number;
}

export interface WarmUpStatus {
  current_stage: WarmUpStage;
  stage_number: number;
  days_in_stage: number;
  progress_percentage: number;
  daily_metrics: {
    messages_sent: number;
    messages_limit: number;
    groups_joined: number;
    groups_limit: number;
    dms_sent: number;
    dms_limit: number;
  };
  health_score: number;
  can_progress: boolean;
  next_stage?: WarmUpStage;
}

export interface WarmUpStageInfo {
  name: WarmUpStage;
  stage_number: number;
  duration_days: number;
  max_messages_per_day: number;
  max_groups: number;
  max_dms_per_day: number;
  allowed_actions: string[];
}

// Analytics Types
export interface DashboardStats {
  total_campaigns: number;
  active_campaigns: number;
  total_groups: number;
  active_groups: number;
  total_leads: number;
  new_leads_today: number;
  total_messages: number;
  messages_today: number;
  warmup_status: WarmUpStatus;
}

export interface ActivityData {
  date: string;
  messages: number;
  leads: number;
  groups_joined: number;
}

export interface CampaignAnalytics {
  campaign_id: string;
  total_messages: number;
  total_leads: number;
  conversion_rate: number;
  messages_by_day: Array<{ date: string; count: number }>;
  leads_by_status: Record<string, number>;
  top_groups: Array<{ group_id: string; title: string; messages: number }>;
  engagement_rate: number;
}

// Settings Types
export interface AppSettings {
  telegram_connected: boolean;
  telegram_phone?: string;
  warmup_enabled: boolean;
  auto_reply_enabled: boolean;
  notification_email?: string;
  api_key_configured: boolean;
}

export interface WarmUpSettings {
  stages: WarmUpStageInfo[];
}

// API Response Types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
