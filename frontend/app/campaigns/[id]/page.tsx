'use client';

import React from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, Play, Pause, Trash2, Edit, Users, MessageSquare, UserCheck } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useCampaign, useActivateCampaign, usePauseCampaign, useDeleteCampaign } from '@/hooks/useCampaigns';
import { useCampaignAnalytics } from '@/hooks/useAnalytics';
import { formatDate, getStatusColor } from '@/lib/utils';
import { Skeleton } from '@/components/ui/skeleton';
import { StatsCard } from '@/components/dashboard/StatsCard';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';

export default function CampaignDetailPage() {
  const params = useParams();
  const router = useRouter();
  const campaignId = params.id as string;

  const { data: campaign, isLoading } = useCampaign(campaignId);
  const { data: analytics } = useCampaignAnalytics(campaignId);
  const activateMutation = useActivateCampaign();
  const pauseMutation = usePauseCampaign();
  const deleteMutation = useDeleteCampaign();

  // Mock data
  const mockCampaign = {
    id: campaignId,
    name: 'Kripto Topluluğu',
    persona_id: '1',
    status: 'active' as const,
    start_date: '2026-02-01',
    target_keywords: ['bitcoin', 'ethereum', 'defi', 'nft'],
    description: 'Kripto para topuluklarında potansiyel müşterileri hedefleyen kampanya.',
    created_at: '2026-02-01',
  };

  const mockAnalytics = {
    campaign_id: campaignId,
    total_messages: 487,
    total_leads: 34,
    conversion_rate: 7.2,
    messages_by_day: [
      { date: '23 Şub', count: 45 },
      { date: '24 Şub', count: 52 },
      { date: '25 Şub', count: 68 },
      { date: '26 Şub', count: 72 },
      { date: '27 Şub', count: 85 },
      { date: '28 Şub', count: 78 },
      { date: '1 Mar', count: 87 },
    ],
    leads_by_status: { new: 12, contacted: 8, engaged: 10, converted: 4 },
    top_groups: [
      { group_id: '1', title: 'Crypto Turkey', messages: 124 },
      { group_id: '2', title: 'Bitcoin Traders', messages: 98 },
      { group_id: '3', title: 'DeFi Masters', messages: 76 },
    ],
    engagement_rate: 15.4,
  };

  const displayCampaign = campaign || mockCampaign;
  const displayAnalytics = analytics || mockAnalytics;

  const handleActivate = async () => {
    try {
      await activateMutation.mutateAsync(campaignId);
    } catch (error) {
      console.error('Failed to activate:', error);
    }
  };

  const handlePause = async () => {
    try {
      await pauseMutation.mutateAsync(campaignId);
    } catch (error) {
      console.error('Failed to pause:', error);
    }
  };

  const handleDelete = async () => {
    if (confirm('Bu kampanyayı silmek istediğinize emin misiniz?')) {
      try {
        await deleteMutation.mutateAsync(campaignId);
        router.push('/campaigns');
      } catch (error) {
        console.error('Failed to delete:', error);
      }
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-64" />
        <div className="grid grid-cols-4 gap-4">
          {Array(4).fill(0).map((_, i) => (
            <Skeleton key={i} className="h-24" />
          ))}
        </div>
        <Skeleton className="h-96" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div className="flex items-center gap-4">
          <Link href="/campaigns">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="h-4 w-4" />
            </Button>
          </Link>
          <div>
            <div className="flex items-center gap-3">
              <h2 className="text-2xl font-bold">{displayCampaign.name}</h2>
              <Badge className={getStatusColor(displayCampaign.status)}>
                {displayCampaign.status === 'active' ? 'Aktif' :
                 displayCampaign.status === 'paused' ? 'Duraklatılmış' : 'Tamamlandı'}
              </Badge>
            </div>
            <p className="text-muted-foreground">{displayCampaign.description}</p>
          </div>
        </div>
        <div className="flex gap-2">
          {displayCampaign.status === 'paused' ? (
            <Button onClick={handleActivate}>
              <Play className="h-4 w-4 mr-2" /> Başlat
            </Button>
          ) : displayCampaign.status === 'active' ? (
            <Button variant="secondary" onClick={handlePause}>
              <Pause className="h-4 w-4 mr-2" /> Duraklat
            </Button>
          ) : null}
          <Button variant="outline">
            <Edit className="h-4 w-4 mr-2" /> Düzenle
          </Button>
          <Button variant="destructive" onClick={handleDelete}>
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatsCard
          title="Toplam Mesaj"
          value={displayAnalytics.total_messages}
          icon={<MessageSquare className="h-6 w-6 text-blue-600" />}
        />
        <StatsCard
          title="Toplam Lead"
          value={displayAnalytics.total_leads}
          icon={<UserCheck className="h-6 w-6 text-green-600" />}
        />
        <StatsCard
          title="Dönüşüm Oranı"
          value={`${displayAnalytics.conversion_rate}%`}
          icon={<Users className="h-6 w-6 text-purple-600" />}
        />
        <StatsCard
          title="Etkileşim Oranı"
          value={`${displayAnalytics.engagement_rate}%`}
          icon={<MessageSquare className="h-6 w-6 text-indigo-600" />}
        />
      </div>

      {/* Tabs */}
      <Tabs defaultValue="analytics" className="space-y-4">
        <TabsList>
          <TabsTrigger value="analytics">Analitik</TabsTrigger>
          <TabsTrigger value="groups">Gruplar</TabsTrigger>
          <TabsTrigger value="leads">Lead'ler</TabsTrigger>
          <TabsTrigger value="settings">Ayarlar</TabsTrigger>
        </TabsList>

        <TabsContent value="analytics" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Messages by Day */}
            <Card>
              <CardHeader>
                <CardTitle>Günlük Mesajlar</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={displayAnalytics.messages_by_day}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Line type="monotone" dataKey="count" stroke="#3b82f6" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            {/* Leads by Status */}
            <Card>
              <CardHeader>
                <CardTitle>Lead Dağılımı</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={Object.entries(displayAnalytics.leads_by_status).map(([status, count]) => ({ status, count }))}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="status" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="count" fill="#10b981" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Top Groups */}
          <Card>
            <CardHeader>
              <CardTitle>En Aktif Gruplar</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {displayAnalytics.top_groups.map((group, i) => (
                  <div key={group.group_id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <span className="font-bold text-muted-foreground">#{i + 1}</span>
                      <span className="font-medium">{group.title}</span>
                    </div>
                    <Badge variant="secondary">{group.messages} mesaj</Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="groups">
          <Card>
            <CardContent className="p-6">
              <p className="text-muted-foreground text-center">Grup yönetimi bu sekmede gösterilecek</p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="leads">
          <Card>
            <CardContent className="p-6">
              <p className="text-muted-foreground text-center">Lead listesi bu sekmede gösterilecek</p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="settings">
          <Card>
            <CardHeader>
              <CardTitle>Kampanya Ayarları</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Anahtar Kelimeler</p>
                <div className="flex flex-wrap gap-2 mt-2">
                  {displayCampaign.target_keywords.map((kw, i) => (
                    <Badge key={i} variant="secondary">{kw}</Badge>
                  ))}
                </div>
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">Başlangıç Tarihi</p>
                <p className="mt-1">{formatDate(displayCampaign.start_date)}</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
