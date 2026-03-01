'use client';

import React, { useState } from 'react';
import { Calendar, Download, TrendingUp, Users, MessageSquare, UserCheck } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useActivityTimeline, usePerformanceSummary, useDashboardStats } from '@/hooks/useAnalytics';
import { useCampaigns } from '@/hooks/useCampaigns';
import { useLeadFunnel } from '@/hooks/useLeads';
import { Skeleton } from '@/components/ui/skeleton';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts';

export default function AnalyticsPage() {
  const [dateRange, setDateRange] = useState('7');

  const { data: activity, isLoading: activityLoading } = useActivityTimeline(parseInt(dateRange));
  const { data: performance } = usePerformanceSummary(parseInt(dateRange));
  const { data: stats } = useDashboardStats();
  const { data: campaigns } = useCampaigns();
  const { data: funnel } = useLeadFunnel();

  // Mock data
  const mockActivity = [
    { date: '23 Şub', messages: 45, leads: 3, groups_joined: 1 },
    { date: '24 Şub', messages: 52, leads: 5, groups_joined: 0 },
    { date: '25 Şub', messages: 61, leads: 4, groups_joined: 2 },
    { date: '26 Şub', messages: 48, leads: 6, groups_joined: 1 },
    { date: '27 Şub', messages: 72, leads: 8, groups_joined: 0 },
    { date: '28 Şub', messages: 85, leads: 10, groups_joined: 1 },
    { date: '1 Mar', messages: 89, leads: 12, groups_joined: 2 },
  ];

  const mockCampaignPerformance = [
    { name: 'Kripto Topluluğu', messages: 487, leads: 34, conversion: 7.2 },
    { name: 'Tech Startup', messages: 312, leads: 28, conversion: 9.0 },
    { name: 'Freelancer Network', messages: 245, leads: 18, conversion: 7.3 },
    { name: 'E-commerce Pilot', messages: 198, leads: 15, conversion: 7.6 },
  ];

  const mockFunnel = { new: 45, contacted: 28, engaged: 18, converted: 12, lost: 8 };

  const mockGroupActivity = [
    { name: 'Crypto Turkey', messages: 124 },
    { name: 'Bitcoin Traders', messages: 98 },
    { name: 'DeFi Masters', messages: 76 },
    { name: 'NFT Community', messages: 65 },
    { name: 'Tech Startups TR', messages: 52 },
  ];

  const displayActivity = activity || mockActivity;
  const displayFunnel = funnel || mockFunnel;

  const COLORS = ['#3b82f6', '#8b5cf6', '#6366f1', '#10b981', '#ef4444'];
  const funnelData = Object.entries(displayFunnel).map(([name, value]) => ({ name, value }));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold">Analitik</h2>
          <p className="text-muted-foreground">Detaylı performans metrikleri</p>
        </div>
        <div className="flex gap-4">
          <Select value={dateRange} onValueChange={setDateRange}>
            <SelectTrigger className="w-40">
              <Calendar className="h-4 w-4 mr-2" />
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7">Son 7 Gün</SelectItem>
              <SelectItem value="14">Son 14 Gün</SelectItem>
              <SelectItem value="30">Son 30 Gün</SelectItem>
              <SelectItem value="90">Son 90 Gün</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" /> Rapor İndir
          </Button>
        </div>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4 flex items-center gap-4">
            <div className="h-12 w-12 rounded-full bg-blue-100 flex items-center justify-center">
              <MessageSquare className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Toplam Mesaj</p>
              <p className="text-2xl font-bold">{displayActivity.reduce((sum, d) => sum + d.messages, 0)}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 flex items-center gap-4">
            <div className="h-12 w-12 rounded-full bg-green-100 flex items-center justify-center">
              <UserCheck className="h-6 w-6 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Yeni Lead</p>
              <p className="text-2xl font-bold">{displayActivity.reduce((sum, d) => sum + d.leads, 0)}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 flex items-center gap-4">
            <div className="h-12 w-12 rounded-full bg-purple-100 flex items-center justify-center">
              <Users className="h-6 w-6 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Katılınan Grup</p>
              <p className="text-2xl font-bold">{displayActivity.reduce((sum, d) => sum + d.groups_joined, 0)}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 flex items-center gap-4">
            <div className="h-12 w-12 rounded-full bg-indigo-100 flex items-center justify-center">
              <TrendingUp className="h-6 w-6 text-indigo-600" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Dönüşüm Oranı</p>
              <p className="text-2xl font-bold">7.8%</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Genel Bakış</TabsTrigger>
          <TabsTrigger value="campaigns">Kampanyalar</TabsTrigger>
          <TabsTrigger value="leads">Lead'ler</TabsTrigger>
          <TabsTrigger value="groups">Gruplar</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          {/* Activity Chart */}
          <Card>
            <CardHeader>
              <CardTitle>Günlük Aktivite</CardTitle>
            </CardHeader>
            <CardContent>
              {activityLoading ? (
                <Skeleton className="h-[300px] w-full" />
              ) : (
                <div className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={displayActivity}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Line type="monotone" dataKey="messages" stroke="#3b82f6" strokeWidth={2} name="Mesajlar" />
                      <Line type="monotone" dataKey="leads" stroke="#10b981" strokeWidth={2} name="Lead'ler" />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="campaigns" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Kampanya Performansı</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={mockCampaignPerformance}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="messages" fill="#3b82f6" name="Mesajlar" />
                    <Bar dataKey="leads" fill="#10b981" name="Lead'ler" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="leads" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Lead Hunisi</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={funnelData}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={100}
                        paddingAngle={5}
                        dataKey="value"
                      >
                        {funnelData.map((_, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Durum Dağılımı</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={funnelData} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis type="number" />
                      <YAxis dataKey="name" type="category" width={100} />
                      <Tooltip />
                      <Bar dataKey="value" fill="#3b82f6" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="groups" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Grup Aktivitesi</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={mockGroupActivity}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="messages" fill="#8b5cf6" name="Mesajlar" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
