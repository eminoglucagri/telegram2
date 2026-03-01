'use client';

import React from 'react';
import { Megaphone, Users, UserCheck, MessageSquare } from 'lucide-react';
import { StatsCard } from '@/components/dashboard/StatsCard';
import { ActivityChart } from '@/components/dashboard/ActivityChart';
import { RecentLeads } from '@/components/dashboard/RecentLeads';
import { WarmupProgress } from '@/components/dashboard/WarmupProgress';
import { useDashboardStats, useActivityTimeline, useWarmupStatus } from '@/hooks/useAnalytics';
import { useLeads } from '@/hooks/useLeads';
import { Skeleton } from '@/components/ui/skeleton';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export default function DashboardPage() {
  const { data: stats, isLoading: statsLoading } = useDashboardStats();
  const { data: activity, isLoading: activityLoading } = useActivityTimeline(7);
  const { data: warmupStatus, isLoading: warmupLoading } = useWarmupStatus();
  const { data: leads, isLoading: leadsLoading } = useLeads({ limit: 5 });

  // Mock data for demo
  const mockStats = {
    total_campaigns: 5,
    active_campaigns: 3,
    total_groups: 24,
    active_groups: 18,
    total_leads: 156,
    new_leads_today: 12,
    total_messages: 1847,
    messages_today: 89,
  };

  const mockActivity = [
    { date: '23 Şub', messages: 45, leads: 3, groups_joined: 1 },
    { date: '24 Şub', messages: 52, leads: 5, groups_joined: 0 },
    { date: '25 Şub', messages: 61, leads: 4, groups_joined: 2 },
    { date: '26 Şub', messages: 48, leads: 6, groups_joined: 1 },
    { date: '27 Şub', messages: 72, leads: 8, groups_joined: 0 },
    { date: '28 Şub', messages: 85, leads: 10, groups_joined: 1 },
    { date: '1 Mar', messages: 89, leads: 12, groups_joined: 2 },
  ];

  const mockWarmup = {
    current_stage: 'participant' as const,
    stage_number: 3,
    days_in_stage: 5,
    progress_percentage: 65,
    daily_metrics: {
      messages_sent: 45,
      messages_limit: 100,
      groups_joined: 2,
      groups_limit: 5,
      dms_sent: 8,
      dms_limit: 20,
    },
    health_score: 85,
    can_progress: false,
    next_stage: 'contributor' as const,
  };

  const mockLeads = [
    { id: '1', telegram_id: 123, username: 'user1', first_name: 'Ahmet', source_group_id: '1', status: 'new' as const, score: 75, created_at: new Date().toISOString() },
    { id: '2', telegram_id: 124, username: 'user2', first_name: 'Mehmet', source_group_id: '2', status: 'contacted' as const, score: 82, created_at: new Date(Date.now() - 3600000).toISOString() },
    { id: '3', telegram_id: 125, username: 'user3', first_name: 'Ayşe', source_group_id: '1', status: 'engaged' as const, score: 90, created_at: new Date(Date.now() - 7200000).toISOString() },
  ];

  const displayStats = stats || mockStats;
  const displayActivity = activity || mockActivity;
  const displayWarmup = warmupStatus || mockWarmup;
  const displayLeads = leads || mockLeads;

  return (
    <div className="space-y-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statsLoading ? (
          Array(4).fill(0).map((_, i) => (
            <Card key={i}>
              <CardContent className="p-6">
                <Skeleton className="h-20 w-full" />
              </CardContent>
            </Card>
          ))
        ) : (
          <>
            <StatsCard
              title="Toplam Kampanya"
              value={displayStats.total_campaigns}
              icon={<Megaphone className="h-6 w-6 text-blue-600" />}
              description={`${displayStats.active_campaigns} aktif`}
            />
            <StatsCard
              title="Aktif Gruplar"
              value={displayStats.active_groups}
              icon={<Users className="h-6 w-6 text-indigo-600" />}
              description={`${displayStats.total_groups} toplam`}
            />
            <StatsCard
              title="Toplam Lead"
              value={displayStats.total_leads}
              icon={<UserCheck className="h-6 w-6 text-green-600" />}
              trend={{ value: 15, isPositive: true }}
              description={`Bugün ${displayStats.new_leads_today} yeni`}
            />
            <StatsCard
              title="Mesajlar"
              value={displayStats.total_messages}
              icon={<MessageSquare className="h-6 w-6 text-purple-600" />}
              description={`Bugün ${displayStats.messages_today}`}
            />
          </>
        )}
      </div>

      {/* Charts and Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Activity Chart - 2 columns */}
        <div className="lg:col-span-2">
          {activityLoading ? (
            <Card>
              <CardHeader>
                <Skeleton className="h-6 w-40" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-[300px] w-full" />
              </CardContent>
            </Card>
          ) : (
            <ActivityChart data={displayActivity} title="Son 7 Gün Aktivite" />
          )}
        </div>

        {/* Warmup Status - 1 column */}
        <div>
          {warmupLoading ? (
            <Card>
              <CardHeader>
                <Skeleton className="h-6 w-40" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-[300px] w-full" />
              </CardContent>
            </Card>
          ) : (
            <WarmupProgress status={displayWarmup} />
          )}
        </div>
      </div>

      {/* Recent Leads */}
      <div>
        {leadsLoading ? (
          <Card>
            <CardHeader>
              <Skeleton className="h-6 w-32" />
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {Array(3).fill(0).map((_, i) => (
                  <Skeleton key={i} className="h-16 w-full" />
                ))}
              </div>
            </CardContent>
          </Card>
        ) : (
          <RecentLeads leads={displayLeads} />
        )}
      </div>
    </div>
  );
}
