import axios, { AxiosError, AxiosInstance } from 'axios';
import {
  Account, InitiateLoginRequest, InitiateLoginResponse, VerifyCodeRequest, AccountStatusResponse,
  Campaign, CampaignCreate, CampaignUpdate,
  Group, GroupCreate, GroupUpdate,
  Message, MessageStats,
  Lead, LeadCreate, LeadUpdate,
  Persona, PersonaCreate, PersonaUpdate,
  DashboardStats, CampaignAnalytics, ActivityData,
  WarmUpStatus, WarmUpStageInfo, WarmUpMetric,
  AppSettings,
} from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      if (typeof window !== 'undefined') {
        localStorage.removeItem('token');
      }
    }
    return Promise.reject(error);
  }
);

// Accounts API
export const accountsAPI = {
  getAll: async (): Promise<Account[]> => {
    const response = await api.get('/api/accounts');
    return response.data;
  },
  getById: async (id: number): Promise<Account> => {
    const response = await api.get(`/api/accounts/${id}`);
    return response.data;
  },
  initiateLogin: async (data: InitiateLoginRequest): Promise<InitiateLoginResponse> => {
    const response = await api.post('/api/accounts/initiate-login', data);
    return response.data;
  },
  verifyCode: async (data: VerifyCodeRequest): Promise<Account> => {
    const response = await api.post('/api/accounts/verify-code', data);
    return response.data;
  },
  getStatus: async (id: number): Promise<AccountStatusResponse> => {
    const response = await api.get(`/api/accounts/${id}/status`);
    return response.data;
  },
  delete: async (id: number): Promise<void> => {
    await api.delete(`/api/accounts/${id}`);
  },
};

// Campaigns API
export const campaignsAPI = {
  getAll: async (status?: string): Promise<Campaign[]> => {
    const params = status ? { status } : {};
    const response = await api.get('/api/campaigns', { params });
    return response.data;
  },
  getById: async (id: string): Promise<Campaign> => {
    const response = await api.get(`/api/campaigns/${id}`);
    return response.data;
  },
  create: async (data: CampaignCreate): Promise<Campaign> => {
    const response = await api.post('/api/campaigns', data);
    return response.data;
  },
  update: async (id: string, data: CampaignUpdate): Promise<Campaign> => {
    const response = await api.put(`/api/campaigns/${id}`, data);
    return response.data;
  },
  delete: async (id: string): Promise<void> => {
    await api.delete(`/api/campaigns/${id}`);
  },
  activate: async (id: string): Promise<Campaign> => {
    const response = await api.post(`/api/campaigns/${id}/activate`);
    return response.data;
  },
  pause: async (id: string): Promise<Campaign> => {
    const response = await api.post(`/api/campaigns/${id}/pause`);
    return response.data;
  },
};

// Groups API
export const groupsAPI = {
  getAll: async (status?: string): Promise<Group[]> => {
    const params = status ? { status } : {};
    const response = await api.get('/api/groups', { params });
    return response.data;
  },
  getById: async (id: string): Promise<Group> => {
    const response = await api.get(`/api/groups/${id}`);
    return response.data;
  },
  create: async (data: GroupCreate): Promise<Group> => {
    const response = await api.post('/api/groups', data);
    return response.data;
  },
  update: async (id: string, data: GroupUpdate): Promise<Group> => {
    const response = await api.put(`/api/groups/${id}`, data);
    return response.data;
  },
  leave: async (id: string): Promise<void> => {
    await api.delete(`/api/groups/${id}`);
  },
  assignToCampaign: async (id: string, campaignId: string): Promise<Group> => {
    const response = await api.post(`/api/groups/${id}/assign`, { campaign_id: campaignId });
    return response.data;
  },
};

// Messages API
export const messagesAPI = {
  getAll: async (params?: {
    group_id?: string;
    campaign_id?: string;
    is_bot?: boolean;
    is_dm?: boolean;
    start_date?: string;
    end_date?: string;
    skip?: number;
    limit?: number;
  }): Promise<Message[]> => {
    const response = await api.get('/api/messages', { params });
    return response.data;
  },
  getById: async (id: string): Promise<Message> => {
    const response = await api.get(`/api/messages/${id}`);
    return response.data;
  },
  getStats: async (params?: {
    group_id?: string;
    campaign_id?: string;
    start_date?: string;
    end_date?: string;
  }): Promise<MessageStats> => {
    const response = await api.get('/api/messages/stats', { params });
    return response.data;
  },
  getConversation: async (groupId: string): Promise<Message[]> => {
    const response = await api.get(`/api/messages/conversation/${groupId}`);
    return response.data;
  },
};

// Leads API
export const leadsAPI = {
  getAll: async (params?: {
    campaign_id?: string;
    status?: string;
    min_score?: number;
    skip?: number;
    limit?: number;
  }): Promise<Lead[]> => {
    const response = await api.get('/api/leads', { params });
    return response.data;
  },
  getById: async (id: string): Promise<Lead> => {
    const response = await api.get(`/api/leads/${id}`);
    return response.data;
  },
  create: async (data: LeadCreate): Promise<Lead> => {
    const response = await api.post('/api/leads', data);
    return response.data;
  },
  update: async (id: string, data: LeadUpdate): Promise<Lead> => {
    const response = await api.put(`/api/leads/${id}`, data);
    return response.data;
  },
  delete: async (id: string): Promise<void> => {
    await api.delete(`/api/leads/${id}`);
  },
  export: async (): Promise<Blob> => {
    const response = await api.get('/api/leads/export', { responseType: 'blob' });
    return response.data;
  },
  getFunnel: async (): Promise<Record<string, number>> => {
    const response = await api.get('/api/leads/funnel');
    return response.data;
  },
};

// Personas API
export const personasAPI = {
  getAll: async (activeOnly?: boolean): Promise<Persona[]> => {
    const params = activeOnly !== undefined ? { active_only: activeOnly } : {};
    const response = await api.get('/api/personas', { params });
    return response.data;
  },
  getById: async (id: string): Promise<Persona> => {
    const response = await api.get(`/api/personas/${id}`);
    return response.data;
  },
  create: async (data: PersonaCreate): Promise<Persona> => {
    const response = await api.post('/api/personas', data);
    return response.data;
  },
  update: async (id: string, data: PersonaUpdate): Promise<Persona> => {
    const response = await api.put(`/api/personas/${id}`, data);
    return response.data;
  },
  delete: async (id: string): Promise<void> => {
    await api.delete(`/api/personas/${id}`);
  },
  preview: async (id: string, sampleMessage?: string): Promise<{ system_prompt: string; should_engage: boolean }> => {
    const response = await api.post(`/api/personas/${id}/preview`, { sample_message: sampleMessage });
    return response.data;
  },
};

// Analytics API
export const analyticsAPI = {
  getDashboard: async (userId?: string): Promise<DashboardStats> => {
    const params = userId ? { user_id: userId } : {};
    const response = await api.get('/api/analytics/dashboard', { params });
    return response.data;
  },
  getCampaignAnalytics: async (campaignId: string, days?: number): Promise<CampaignAnalytics> => {
    const params = days ? { days } : {};
    const response = await api.get(`/api/analytics/campaign/${campaignId}`, { params });
    return response.data;
  },
  getActivityTimeline: async (days?: number): Promise<ActivityData[]> => {
    const params = days ? { days } : {};
    const response = await api.get('/api/analytics/activity', { params });
    return response.data;
  },
  getPerformanceSummary: async (days?: number): Promise<{ messages: number[]; leads: number[]; dates: string[] }> => {
    const params = days ? { days } : {};
    const response = await api.get('/api/analytics/performance', { params });
    return response.data;
  },
};

// WarmUp API
export const warmupAPI = {
  getStatus: async (userId?: string): Promise<WarmUpStatus> => {
    const params = userId ? { user_id: userId } : {};
    const response = await api.get('/api/warmup/status', { params });
    return response.data;
  },
  getStages: async (): Promise<WarmUpStageInfo[]> => {
    const response = await api.get('/api/warmup/stages');
    return response.data;
  },
  getHistory: async (userId?: string, days?: number): Promise<WarmUpMetric[]> => {
    const params: Record<string, unknown> = {};
    if (userId) params.user_id = userId;
    if (days) params.days = days;
    const response = await api.get('/api/warmup/history', { params });
    return response.data;
  },
  checkAction: async (action: string, userId?: string): Promise<{ allowed: boolean; reason?: string }> => {
    const params: Record<string, unknown> = { action };
    if (userId) params.user_id = userId;
    const response = await api.get('/api/warmup/check-action', { params });
    return response.data;
  },
  progressStage: async (userId?: string): Promise<WarmUpStatus> => {
    const data = userId ? { user_id: userId } : {};
    const response = await api.post('/api/warmup/progress', data);
    return response.data;
  },
};

// Settings API
export const settingsAPI = {
  get: async (): Promise<AppSettings> => {
    const response = await api.get('/api/settings');
    return response.data;
  },
  update: async (data: Partial<AppSettings>): Promise<AppSettings> => {
    const response = await api.put('/api/settings', data);
    return response.data;
  },
  health: async (): Promise<{ status: string; services: Record<string, boolean> }> => {
    const response = await api.get('/api/settings/health');
    return response.data;
  },
};

export default api;
