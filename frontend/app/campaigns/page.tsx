'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { Plus, Search, Filter, Play, Pause, Trash2, Eye, MoreHorizontal } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import { useCampaigns, useActivateCampaign, usePauseCampaign, useDeleteCampaign } from '@/hooks/useCampaigns';
import { formatDate, getStatusColor } from '@/lib/utils';
import { Skeleton } from '@/components/ui/skeleton';
import { Campaign } from '@/lib/types';

export default function CampaignsPage() {
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');

  const { data: campaigns, isLoading } = useCampaigns(statusFilter || undefined);
  const activateMutation = useActivateCampaign();
  const pauseMutation = usePauseCampaign();
  const deleteMutation = useDeleteCampaign();

  // Mock data for demo
  const mockCampaigns: Campaign[] = [
    { id: '1', name: 'Kripto Topluluğu', persona_id: '1', status: 'active', start_date: '2026-02-01', target_keywords: ['bitcoin', 'ethereum'], created_at: '2026-02-01' },
    { id: '2', name: 'Tech Startup', persona_id: '2', status: 'active', start_date: '2026-02-10', target_keywords: ['startup', 'saas'], created_at: '2026-02-10' },
    { id: '3', name: 'Freelancer Network', persona_id: '1', status: 'paused', start_date: '2026-01-15', target_keywords: ['freelance', 'remote'], created_at: '2026-01-15' },
    { id: '4', name: 'E-commerce Pilot', persona_id: '3', status: 'completed', start_date: '2026-01-01', end_date: '2026-02-01', target_keywords: ['ecommerce', 'dropshipping'], created_at: '2026-01-01' },
  ];

  const displayCampaigns = campaigns || mockCampaigns;

  const filteredCampaigns = displayCampaigns.filter(campaign =>
    campaign.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleActivate = async (id: string) => {
    try {
      await activateMutation.mutateAsync(id);
    } catch (error) {
      console.error('Failed to activate campaign:', error);
    }
  };

  const handlePause = async (id: string) => {
    try {
      await pauseMutation.mutateAsync(id);
    } catch (error) {
      console.error('Failed to pause campaign:', error);
    }
  };

  const handleDelete = async (id: string) => {
    if (confirm('Bu kampanyayı silmek istediğinize emin misiniz?')) {
      try {
        await deleteMutation.mutateAsync(id);
      } catch (error) {
        console.error('Failed to delete campaign:', error);
      }
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold">Kampanyalar</h2>
          <p className="text-muted-foreground">Tüm marketing kampanyalarınızı yönetin</p>
        </div>
        <Link href="/campaigns/new">
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Yeni Kampanya
          </Button>
        </Link>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Kampanya ara..."
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
                <SelectItem value="paused">Duraklatılmış</SelectItem>
                <SelectItem value="completed">Tamamlandı</SelectItem>
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
              {Array(4).fill(0).map((_, i) => (
                <Skeleton key={i} className="h-12 w-full" />
              ))}
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Kampanya Adı</TableHead>
                  <TableHead>Durum</TableHead>
                  <TableHead>Anahtar Kelimeler</TableHead>
                  <TableHead>Başlangıç</TableHead>
                  <TableHead>Bitiş</TableHead>
                  <TableHead className="text-right">İşlemler</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredCampaigns.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center py-8 text-muted-foreground">
                      Henüz kampanya bulunmuyor
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredCampaigns.map((campaign) => (
                    <TableRow key={campaign.id}>
                      <TableCell className="font-medium">{campaign.name}</TableCell>
                      <TableCell>
                        <Badge className={getStatusColor(campaign.status)}>
                          {campaign.status === 'active' ? 'Aktif' :
                           campaign.status === 'paused' ? 'Duraklatılmış' :
                           campaign.status === 'completed' ? 'Tamamlandı' : 'Taslak'}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex flex-wrap gap-1">
                          {campaign.target_keywords.slice(0, 3).map((kw, i) => (
                            <Badge key={i} variant="outline" className="text-xs">
                              {kw}
                            </Badge>
                          ))}
                          {campaign.target_keywords.length > 3 && (
                            <Badge variant="outline" className="text-xs">
                              +{campaign.target_keywords.length - 3}
                            </Badge>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>{formatDate(campaign.start_date)}</TableCell>
                      <TableCell>{campaign.end_date ? formatDate(campaign.end_date) : '-'}</TableCell>
                      <TableCell className="text-right">
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="icon">
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <Link href={`/campaigns/${campaign.id}`}>
                              <DropdownMenuItem>
                                <Eye className="h-4 w-4 mr-2" />
                                Detay
                              </DropdownMenuItem>
                            </Link>
                            {campaign.status === 'paused' ? (
                              <DropdownMenuItem onClick={() => handleActivate(campaign.id)}>
                                <Play className="h-4 w-4 mr-2" />
                                Başlat
                              </DropdownMenuItem>
                            ) : campaign.status === 'active' ? (
                              <DropdownMenuItem onClick={() => handlePause(campaign.id)}>
                                <Pause className="h-4 w-4 mr-2" />
                                Duraklat
                              </DropdownMenuItem>
                            ) : null}
                            <DropdownMenuItem
                              className="text-red-600"
                              onClick={() => handleDelete(campaign.id)}
                            >
                              <Trash2 className="h-4 w-4 mr-2" />
                              Sil
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
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
