'use client';

import React, { useState } from 'react';
import { Save, Shield, Bell, Key, Trash2, AlertTriangle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { useWarmupStatus, useWarmupStages } from '@/hooks/useAnalytics';
import { WarmUpStageInfo } from '@/lib/types';

export default function SettingsPage() {
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [autoReplyEnabled, setAutoReplyEnabled] = useState(true);
  const [warmupEnabled, setWarmupEnabled] = useState(true);

  const { data: warmupStatus } = useWarmupStatus();
  const { data: warmupStages } = useWarmupStages();

  // Mock data
  const mockWarmupStages: WarmUpStageInfo[] = [
    { name: 'observer', stage_number: 1, duration_days: 3, max_messages_per_day: 10, max_groups: 2, max_dms_per_day: 0, allowed_actions: ['read', 'react'] },
    { name: 'reactor', stage_number: 2, duration_days: 4, max_messages_per_day: 25, max_groups: 5, max_dms_per_day: 3, allowed_actions: ['read', 'react', 'reply'] },
    { name: 'participant', stage_number: 3, duration_days: 5, max_messages_per_day: 50, max_groups: 10, max_dms_per_day: 10, allowed_actions: ['read', 'react', 'reply', 'initiate'] },
    { name: 'contributor', stage_number: 4, duration_days: 7, max_messages_per_day: 100, max_groups: 20, max_dms_per_day: 25, allowed_actions: ['read', 'react', 'reply', 'initiate', 'dm'] },
    { name: 'influencer', stage_number: 5, duration_days: 0, max_messages_per_day: 200, max_groups: 50, max_dms_per_day: 50, allowed_actions: ['all'] },
  ];

  const displayStages = warmupStages || mockWarmupStages;

  const mockWarmupStatus = {
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
  };

  const displayWarmupStatus = warmupStatus || mockWarmupStatus;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold">Ayarlar</h2>
        <p className="text-muted-foreground">Uygulama ayarlarını yönetin</p>
      </div>

      <Tabs defaultValue="account" className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="account">Hesap</TabsTrigger>
          <TabsTrigger value="warmup">Warm-up</TabsTrigger>
          <TabsTrigger value="notifications">Bildirimler</TabsTrigger>
          <TabsTrigger value="danger">Tehlikeli</TabsTrigger>
        </TabsList>

        {/* Account Tab */}
        <TabsContent value="account" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                Telegram Hesabı
              </CardTitle>
              <CardDescription>Bağlı Telegram hesap bilgileri</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-muted-foreground">Telefon</Label>
                  <p className="font-medium">+90 *** *** ** 45</p>
                </div>
                <div>
                  <Label className="text-muted-foreground">Durum</Label>
                  <Badge className="bg-green-100 text-green-800">Bağlı</Badge>
                </div>
                <div>
                  <Label className="text-muted-foreground">Session</Label>
                  <p className="font-medium text-muted-foreground">Aktif</p>
                </div>
                <div>
                  <Label className="text-muted-foreground">Son Aktivite</Label>
                  <p className="font-medium">Az önce</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Key className="h-5 w-5" />
                API Anahtarları
              </CardTitle>
              <CardDescription>Entegrasyon anahtarları</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>OpenAI API Key</Label>
                <div className="flex gap-2">
                  <Input type="password" value="sk-**************************" readOnly />
                  <Button variant="outline">Değiştir</Button>
                </div>
              </div>
              <div className="space-y-2">
                <Label>Telegram API ID</Label>
                <Input value="12345678" readOnly className="bg-gray-50" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Genel Ayarlar</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Otomatik Yanıt</p>
                  <p className="text-sm text-muted-foreground">Mesajlara otomatik yanıt ver</p>
                </div>
                <Switch checked={autoReplyEnabled} onCheckedChange={setAutoReplyEnabled} />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Warm-up Modu</p>
                  <p className="text-sm text-muted-foreground">Hesap ısınma protokolünü etkinleştir</p>
                </div>
                <Switch checked={warmupEnabled} onCheckedChange={setWarmupEnabled} />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Warmup Tab */}
        <TabsContent value="warmup" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Mevcut Durum</CardTitle>
              <CardDescription>Hesabınızın warm-up durumu</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Mevcut Aşama</p>
                  <p className="text-xl font-bold capitalize">{displayWarmupStatus.current_stage}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-muted-foreground">Sağlık Skoru</p>
                  <p className={`text-xl font-bold ${
                    displayWarmupStatus.health_score >= 80 ? 'text-green-600' :
                    displayWarmupStatus.health_score >= 50 ? 'text-yellow-600' : 'text-red-600'
                  }`}>{displayWarmupStatus.health_score}%</p>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span>Aşama İlerlemesi</span>
                  <span>{displayWarmupStatus.progress_percentage}%</span>
                </div>
                <Progress value={displayWarmupStatus.progress_percentage} />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Warm-up Aşamaları</CardTitle>
              <CardDescription>Her aşamanın limitleri ve süreleri</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {displayStages.map((stage, index) => (
                  <div
                    key={stage.name}
                    className={`p-4 rounded-lg border ${
                      index + 1 < displayWarmupStatus.stage_number ? 'bg-green-50 border-green-200' :
                      index + 1 === displayWarmupStatus.stage_number ? 'bg-blue-50 border-blue-200' :
                      'bg-gray-50 border-gray-200'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Badge variant={index + 1 <= displayWarmupStatus.stage_number ? 'default' : 'secondary'}>
                          Aşama {stage.stage_number}
                        </Badge>
                        <span className="font-medium capitalize">{stage.name}</span>
                      </div>
                      <span className="text-sm text-muted-foreground">
                        {stage.duration_days > 0 ? `${stage.duration_days} gün` : 'Süresiz'}
                      </span>
                    </div>
                    <div className="grid grid-cols-3 gap-4 text-sm">
                      <div>
                        <p className="text-muted-foreground">Mesaj/Gün</p>
                        <p className="font-medium">{stage.max_messages_per_day}</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Max Grup</p>
                        <p className="font-medium">{stage.max_groups}</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">DM/Gün</p>
                        <p className="font-medium">{stage.max_dms_per_day}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Notifications Tab */}
        <TabsContent value="notifications" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bell className="h-5 w-5" />
                Bildirim Ayarları
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Email Bildirimleri</p>
                  <p className="text-sm text-muted-foreground">Önemli olaylar için email al</p>
                </div>
                <Switch checked={notificationsEnabled} onCheckedChange={setNotificationsEnabled} />
              </div>
              <div className="space-y-2">
                <Label>Email Adresi</Label>
                <Input type="email" placeholder="email@example.com" />
              </div>
              <Button>
                <Save className="h-4 w-4 mr-2" /> Kaydet
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Danger Tab */}
        <TabsContent value="danger" className="space-y-4">
          <Alert variant="destructive">
            <AlertTriangle className="h-4 w-4" />
            <AlertTitle>Dikkat!</AlertTitle>
            <AlertDescription>
              Bu bölümdeki işlemler geri alınamaz. Lütfen dikkatli olun.
            </AlertDescription>
          </Alert>

          <Card className="border-red-200">
            <CardHeader>
              <CardTitle className="text-red-600 flex items-center gap-2">
                <Trash2 className="h-5 w-5" />
                Verileri Sıfırla
              </CardTitle>
              <CardDescription>
                Tüm mesaj geçmişini, lead'leri ve analitik verilerini sil
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button variant="destructive">
                <Trash2 className="h-4 w-4 mr-2" /> Tüm Verileri Sil
              </Button>
            </CardContent>
          </Card>

          <Card className="border-red-200">
            <CardHeader>
              <CardTitle className="text-red-600 flex items-center gap-2">
                <AlertTriangle className="h-5 w-5" />
                Hesabı Sil
              </CardTitle>
              <CardDescription>
                Telegram bağlantısını kes ve tüm verileri kalıcı olarak sil
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button variant="destructive">
                <Trash2 className="h-4 w-4 mr-2" /> Hesabı Sil
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
