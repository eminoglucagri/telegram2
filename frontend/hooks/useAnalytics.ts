import { useQuery } from '@tanstack/react-query';
import { analyticsAPI, warmupAPI, messagesAPI } from '@/lib/api';
import { DashboardStats, CampaignAnalytics, ActivityData, WarmUpStatus, WarmUpStageInfo, MessageStats } from '@/lib/types';

export const useDashboardStats = (userId?: string) => {
  return useQuery<DashboardStats>({
    queryKey: ['dashboard', userId],
    queryFn: () => analyticsAPI.getDashboard(userId),
    refetchInterval: 60000, // Refresh every minute
  });
};

export const useCampaignAnalytics = (campaignId: string, days?: number) => {
  return useQuery<CampaignAnalytics>({
    queryKey: ['analytics', 'campaign', campaignId, days],
    queryFn: () => analyticsAPI.getCampaignAnalytics(campaignId, days),
    enabled: !!campaignId,
  });
};

export const useActivityTimeline = (days: number = 7) => {
  return useQuery<ActivityData[]>({
    queryKey: ['analytics', 'activity', days],
    queryFn: () => analyticsAPI.getActivityTimeline(days),
  });
};

export const usePerformanceSummary = (days: number = 30) => {
  return useQuery<{ messages: number[]; leads: number[]; dates: string[] }>({
    queryKey: ['analytics', 'performance', days],
    queryFn: () => analyticsAPI.getPerformanceSummary(days),
  });
};

export const useWarmupStatus = (userId?: string) => {
  return useQuery<WarmUpStatus>({
    queryKey: ['warmup', 'status', userId],
    queryFn: () => warmupAPI.getStatus(userId),
    refetchInterval: 60000,
  });
};

export const useWarmupStages = () => {
  return useQuery<WarmUpStageInfo[]>({
    queryKey: ['warmup', 'stages'],
    queryFn: () => warmupAPI.getStages(),
  });
};

export const useMessageStats = (params?: {
  group_id?: string;
  campaign_id?: string;
  start_date?: string;
  end_date?: string;
}) => {
  return useQuery<MessageStats>({
    queryKey: ['messages', 'stats', params],
    queryFn: () => messagesAPI.getStats(params),
  });
};
