'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { WarmUpStatus } from '@/lib/types';
import { Flame, MessageSquare, Users, Send } from 'lucide-react';
import { getStatusColor } from '@/lib/utils';

interface WarmupProgressProps {
  status: WarmUpStatus;
}

export function WarmupProgress({ status }: WarmupProgressProps) {
  const stages = ['observer', 'reactor', 'participant', 'contributor', 'influencer'];

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Flame className="h-5 w-5 text-orange-500" />
            Warm-up Durumu
          </CardTitle>
          <Badge className={getStatusColor(status.current_stage)}>
            {status.current_stage}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Stage Progress */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Aşama İlerlemesi</span>
            <span className="font-medium">{status.progress_percentage}%</span>
          </div>
          <Progress value={status.progress_percentage} className="h-3" />
          <div className="flex justify-between">
            {stages.map((stage, index) => (
              <div
                key={stage}
                className={`text-xs ${index < status.stage_number ? 'text-blue-600 font-medium' : 'text-muted-foreground'}`}
              >
                {index + 1}
              </div>
            ))}
          </div>
        </div>

        {/* Daily Metrics */}
        <div className="space-y-3">
          <p className="text-sm font-medium">Günlük Limitler</p>
          
          {/* Messages */}
          <div className="space-y-1">
            <div className="flex items-center justify-between text-sm">
              <span className="flex items-center gap-2 text-muted-foreground">
                <MessageSquare className="h-4 w-4" />
                Mesajlar
              </span>
              <span>
                {status.daily_metrics.messages_sent} / {status.daily_metrics.messages_limit}
              </span>
            </div>
            <Progress
              value={(status.daily_metrics.messages_sent / status.daily_metrics.messages_limit) * 100}
              className="h-2"
            />
          </div>

          {/* Groups */}
          <div className="space-y-1">
            <div className="flex items-center justify-between text-sm">
              <span className="flex items-center gap-2 text-muted-foreground">
                <Users className="h-4 w-4" />
                Gruplar
              </span>
              <span>
                {status.daily_metrics.groups_joined} / {status.daily_metrics.groups_limit}
              </span>
            </div>
            <Progress
              value={(status.daily_metrics.groups_joined / status.daily_metrics.groups_limit) * 100}
              className="h-2"
            />
          </div>

          {/* DMs */}
          <div className="space-y-1">
            <div className="flex items-center justify-between text-sm">
              <span className="flex items-center gap-2 text-muted-foreground">
                <Send className="h-4 w-4" />
                DM'ler
              </span>
              <span>
                {status.daily_metrics.dms_sent} / {status.daily_metrics.dms_limit}
              </span>
            </div>
            <Progress
              value={(status.daily_metrics.dms_sent / status.daily_metrics.dms_limit) * 100}
              className="h-2"
            />
          </div>
        </div>

        {/* Health Score */}
        <div className="pt-4 border-t">
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">Sağlık Skoru</span>
            <span className={`text-lg font-bold ${
              status.health_score >= 80 ? 'text-green-600' :
              status.health_score >= 50 ? 'text-yellow-600' : 'text-red-600'
            }`}>
              {status.health_score}%
            </span>
          </div>
        </div>

        {status.can_progress && status.next_stage && (
          <div className="bg-green-50 rounded-lg p-3">
            <p className="text-sm text-green-700">
              🎉 Bir sonraki aşamaya geçmeye hazırsınız: <strong>{status.next_stage}</strong>
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
