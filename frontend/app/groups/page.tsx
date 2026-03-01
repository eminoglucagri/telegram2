'use client';

import React, { useState } from 'react';
import { Plus, Search, Users, LogOut, ExternalLink } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useGroups, useAddGroup, useLeaveGroup } from '@/hooks/useGroups';
import { formatDate, formatNumber, getStatusColor } from '@/lib/utils';
import { Skeleton } from '@/components/ui/skeleton';
import { Group } from '@/lib/types';

export default function GroupsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [newGroupUsername, setNewGroupUsername] = useState('');

  const { data: groups, isLoading } = useGroups(statusFilter || undefined);
  const addGroupMutation = useAddGroup();
  const leaveGroupMutation = useLeaveGroup();

  // Mock data
  const mockGroups: Group[] = [
    { id: '1', telegram_id: -1001234567890, title: 'Crypto Turkey', username: 'cryptoturkey', member_count: 15420, joined_at: '2026-02-15', status: 'active' },
    { id: '2', telegram_id: -1001234567891, title: 'Bitcoin Traders', username: 'btctraders', member_count: 8750, joined_at: '2026-02-10', status: 'active' },
    { id: '3', telegram_id: -1001234567892, title: 'DeFi Masters', username: 'defimasters', member_count: 5230, joined_at: '2026-02-05', status: 'active' },
    { id: '4', telegram_id: -1001234567893, title: 'NFT Community', username: 'nftcommunity', member_count: 12400, joined_at: '2026-01-20', status: 'left' },
    { id: '5', telegram_id: -1001234567894, title: 'Tech Startups TR', username: 'techstartups', member_count: 3200, joined_at: '2026-02-20', status: 'active' },
  ];

  const displayGroups = groups || mockGroups;

  const filteredGroups = displayGroups.filter(group =>
    group.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (group.username && group.username.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  const handleAddGroup = async () => {
    if (!newGroupUsername.trim()) return;
    try {
      await addGroupMutation.mutateAsync({ username: newGroupUsername });
      setIsAddDialogOpen(false);
      setNewGroupUsername('');
    } catch (error) {
      console.error('Failed to add group:', error);
    }
  };

  const handleLeaveGroup = async (id: string) => {
    if (confirm('Bu gruptan ayrılmak istediğinize emin misiniz?')) {
      try {
        await leaveGroupMutation.mutateAsync(id);
      } catch (error) {
        console.error('Failed to leave group:', error);
      }
    }
  };

  const activeCount = displayGroups.filter(g => g.status === 'active').length;
  const totalMembers = displayGroups.reduce((sum, g) => sum + g.member_count, 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold">Gruplar</h2>
          <p className="text-muted-foreground">Katıldığınız Telegram grupları</p>
        </div>
        <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Grup Ekle
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Yeni Grup Ekle</DialogTitle>
              <DialogDescription>
                Grubun kullanıcı adını veya davet linkini girin
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="username">Grup Kullanıcı Adı</Label>
                <Input
                  id="username"
                  placeholder="@grupadi veya t.me/grupadi"
                  value={newGroupUsername}
                  onChange={(e) => setNewGroupUsername(e.target.value)}
                />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsAddDialogOpen(false)}>
                Vazgeç
              </Button>
              <Button onClick={handleAddGroup} disabled={addGroupMutation.isPending}>
                {addGroupMutation.isPending ? 'Ekleniyor...' : 'Gruba Katıl'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-4 flex items-center gap-4">
            <div className="h-12 w-12 rounded-full bg-blue-100 flex items-center justify-center">
              <Users className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Toplam Grup</p>
              <p className="text-2xl font-bold">{displayGroups.length}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 flex items-center gap-4">
            <div className="h-12 w-12 rounded-full bg-green-100 flex items-center justify-center">
              <Users className="h-6 w-6 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Aktif Grup</p>
              <p className="text-2xl font-bold">{activeCount}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 flex items-center gap-4">
            <div className="h-12 w-12 rounded-full bg-purple-100 flex items-center justify-center">
              <Users className="h-6 w-6 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Toplam Üye</p>
              <p className="text-2xl font-bold">{formatNumber(totalMembers)}</p>
            </div>
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
                placeholder="Grup ara..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9"
              />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-full sm:w-40">
                <SelectValue placeholder="Durum" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tümü</SelectItem>
                <SelectItem value="active">Aktif</SelectItem>
                <SelectItem value="left">Ayrıldı</SelectItem>
                <SelectItem value="banned">Yasaklı</SelectItem>
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
                <Skeleton key={i} className="h-12 w-full" />
              ))}
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Grup</TableHead>
                  <TableHead>Üye Sayısı</TableHead>
                  <TableHead>Durum</TableHead>
                  <TableHead>Katılım</TableHead>
                  <TableHead className="text-right">İşlemler</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredGroups.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={5} className="text-center py-8 text-muted-foreground">
                      Henüz grup bulunmuyor
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredGroups.map((group) => (
                    <TableRow key={group.id}>
                      <TableCell>
                        <div>
                          <p className="font-medium">{group.title}</p>
                          {group.username && (
                            <p className="text-sm text-muted-foreground">@{group.username}</p>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>{formatNumber(group.member_count)}</TableCell>
                      <TableCell>
                        <Badge className={getStatusColor(group.status)}>
                          {group.status === 'active' ? 'Aktif' :
                           group.status === 'left' ? 'Ayrıldı' : 'Yasaklı'}
                        </Badge>
                      </TableCell>
                      <TableCell>{formatDate(group.joined_at)}</TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          {group.username && (
                            <Button variant="ghost" size="icon" asChild>
                              <a href={`https://t.me/${group.username}`} target="_blank" rel="noopener noreferrer">
                                <ExternalLink className="h-4 w-4" />
                              </a>
                            </Button>
                          )}
                          {group.status === 'active' && (
                            <Button
                              variant="ghost"
                              size="icon"
                              className="text-red-600 hover:text-red-700"
                              onClick={() => handleLeaveGroup(group.id)}
                            >
                              <LogOut className="h-4 w-4" />
                            </Button>
                          )}
                        </div>
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
