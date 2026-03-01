'use client';

import React, { useState } from 'react';
import { Search, Filter, Bot, User } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useMessages } from '@/hooks/useMessages';
import { useGroups } from '@/hooks/useGroups';
import { formatDateTime, truncateText, getStatusColor } from '@/lib/utils';
import { Skeleton } from '@/components/ui/skeleton';
import { Message, Group } from '@/lib/types';

export default function MessagesPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [groupFilter, setGroupFilter] = useState('');
  const [botFilter, setBotFilter] = useState<string>('');

  const { data: messages, isLoading } = useMessages({
    group_id: groupFilter || undefined,
    is_bot: botFilter === 'bot' ? true : botFilter === 'user' ? false : undefined,
    limit: 50,
  });
  const { data: groups } = useGroups();

  // Mock data
  const mockMessages: Message[] = [
    { id: '1', telegram_id: 1, group_id: '1', sender_id: 123, sender_username: 'cryptofan', content: 'Bitcoin bu yıl 100k olur mu sizce?', is_bot_message: false, is_dm: false, sentiment: 'positive', intent: 'question', created_at: new Date().toISOString() },
    { id: '2', telegram_id: 2, group_id: '1', sender_id: 0, sender_username: 'bot', content: 'Piyasa koşullarına bağlı, ama potansiyeli var. Sen ne düşünüyorsun?', is_bot_message: true, is_dm: false, sentiment: 'neutral', intent: 'statement', created_at: new Date(Date.now() - 60000).toISOString() },
    { id: '3', telegram_id: 3, group_id: '2', sender_id: 456, sender_username: 'trader_ali', content: 'ETH pozisyonumu artırdım', is_bot_message: false, is_dm: false, sentiment: 'positive', intent: 'statement', created_at: new Date(Date.now() - 120000).toISOString() },
    { id: '4', telegram_id: 4, group_id: '2', sender_id: 0, sender_username: 'bot', content: 'Güzel hamle! ETH ekosistemi gerçekten gelişiyor.', is_bot_message: true, is_dm: false, sentiment: 'positive', intent: 'statement', created_at: new Date(Date.now() - 180000).toISOString() },
    { id: '5', telegram_id: 5, group_id: '3', sender_id: 789, sender_username: 'defi_master', content: 'Yeni DeFi projeleri hakkında bilgi verir misiniz?', is_bot_message: false, is_dm: false, sentiment: 'neutral', intent: 'question', created_at: new Date(Date.now() - 240000).toISOString() },
  ];

  const mockGroups: Group[] = [
    { id: '1', telegram_id: -1001234567890, title: 'Crypto Turkey', member_count: 15420, joined_at: '2026-02-15', status: 'active' },
    { id: '2', telegram_id: -1001234567891, title: 'Bitcoin Traders', member_count: 8750, joined_at: '2026-02-10', status: 'active' },
    { id: '3', telegram_id: -1001234567892, title: 'DeFi Masters', member_count: 5230, joined_at: '2026-02-05', status: 'active' },
  ];

  const displayMessages = messages || mockMessages;
  const displayGroups = groups || mockGroups;

  const getGroupName = (groupId: string) => {
    const group = displayGroups.find(g => g.id === groupId);
    return group?.title || 'Bilinmeyen Grup';
  };

  const filteredMessages = displayMessages.filter(msg =>
    msg.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (msg.sender_username && msg.sender_username.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold">Mesajlar</h2>
        <p className="text-muted-foreground">Tüm mesaj geçmişi</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-muted-foreground">Toplam Mesaj</p>
            <p className="text-2xl font-bold">{displayMessages.length}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-muted-foreground">Bot Mesajları</p>
            <p className="text-2xl font-bold">{displayMessages.filter(m => m.is_bot_message).length}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-muted-foreground">Kullanıcı Mesajları</p>
            <p className="text-2xl font-bold">{displayMessages.filter(m => !m.is_bot_message).length}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-muted-foreground">DM'ler</p>
            <p className="text-2xl font-bold">{displayMessages.filter(m => m.is_dm).length}</p>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Mesaj ara..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9"
              />
            </div>
            <Select value={groupFilter} onValueChange={setGroupFilter}>
              <SelectTrigger className="w-full sm:w-48">
                <SelectValue placeholder="Grup" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tüm Gruplar</SelectItem>
                {displayGroups.map(group => (
                  <SelectItem key={group.id} value={group.id}>{group.title}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={botFilter} onValueChange={setBotFilter}>
              <SelectTrigger className="w-full sm:w-40">
                <SelectValue placeholder="Gönderen" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tümü</SelectItem>
                <SelectItem value="bot">Bot</SelectItem>
                <SelectItem value="user">Kullanıcı</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Table */}
      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="p-6 space-y-4">
              {Array(5).fill(0).map((_, i) => (
                <Skeleton key={i} className="h-16 w-full" />
              ))}
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Gönderen</TableHead>
                  <TableHead>Mesaj</TableHead>
                  <TableHead>Grup</TableHead>
                  <TableHead>Duygu</TableHead>
                  <TableHead>Tarih</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredMessages.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={5} className="text-center py-8 text-muted-foreground">
                      Mesaj bulunamadı
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredMessages.map((message) => (
                    <TableRow key={message.id}>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <div className={`h-8 w-8 rounded-full flex items-center justify-center ${message.is_bot_message ? 'bg-blue-100' : 'bg-gray-100'}`}>
                            {message.is_bot_message ? (
                              <Bot className="h-4 w-4 text-blue-600" />
                            ) : (
                              <User className="h-4 w-4 text-gray-600" />
                            )}
                          </div>
                          <span className="font-medium">
                            {message.is_bot_message ? 'Bot' : `@${message.sender_username || 'anonim'}`}
                          </span>
                        </div>
                      </TableCell>
                      <TableCell className="max-w-md">
                        <p className="truncate">{truncateText(message.content, 80)}</p>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline">{getGroupName(message.group_id)}</Badge>
                      </TableCell>
                      <TableCell>
                        {message.sentiment && (
                          <Badge className={getStatusColor(
                            message.sentiment === 'positive' ? 'converted' :
                            message.sentiment === 'negative' ? 'lost' : 'pending'
                          )}>
                            {message.sentiment === 'positive' ? 'Pozitif' :
                             message.sentiment === 'negative' ? 'Negatif' : 'Nötr'}
                          </Badge>
                        )}
                      </TableCell>
                      <TableCell className="text-sm text-muted-foreground">
                        {formatDateTime(message.created_at)}
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
