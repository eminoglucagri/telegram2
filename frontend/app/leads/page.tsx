'use client';

import React, { useState } from 'react';
import { Search, Download, Eye, MessageCircle, Trash2, MoreHorizontal } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { useLeads, useUpdateLead, useDeleteLead, useLeadFunnel } from '@/hooks/useLeads';
import { formatDate, formatRelativeTime, getStatusColor, generateCSV } from '@/lib/utils';
import { Skeleton } from '@/components/ui/skeleton';
import { Lead } from '@/lib/types';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

export default function LeadsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null);

  const { data: leads, isLoading } = useLeads({ status: statusFilter || undefined });
  const { data: funnel } = useLeadFunnel();
  const updateMutation = useUpdateLead();
  const deleteMutation = useDeleteLead();

  // Mock data
  const mockLeads: Lead[] = [
    { id: '1', telegram_id: 123456, username: 'cryptofan', first_name: 'Ahmet', source_group_id: '1', source_group_title: 'Crypto Turkey', status: 'new', score: 85, created_at: new Date().toISOString() },
    { id: '2', telegram_id: 123457, username: 'trader_ali', first_name: 'Ali', source_group_id: '2', source_group_title: 'Bitcoin Traders', status: 'contacted', score: 72, contacted_at: new Date(Date.now() - 86400000).toISOString(), created_at: new Date(Date.now() - 172800000).toISOString() },
    { id: '3', telegram_id: 123458, username: 'defi_master', first_name: 'Mehmet', source_group_id: '3', source_group_title: 'DeFi Masters', status: 'engaged', score: 90, created_at: new Date(Date.now() - 259200000).toISOString() },
    { id: '4', telegram_id: 123459, username: 'btc_hodler', first_name: 'Can', source_group_id: '1', source_group_title: 'Crypto Turkey', status: 'converted', score: 95, created_at: new Date(Date.now() - 604800000).toISOString() },
    { id: '5', telegram_id: 123460, username: 'nft_collector', first_name: 'Zeynep', source_group_id: '2', source_group_title: 'Bitcoin Traders', status: 'new', score: 68, created_at: new Date(Date.now() - 3600000).toISOString() },
  ];

  const mockFunnel = { new: 45, contacted: 28, engaged: 18, converted: 12, lost: 8 };

  const displayLeads = leads || mockLeads;
  const displayFunnel = funnel || mockFunnel;

  const filteredLeads = displayLeads.filter(lead =>
    (lead.username && lead.username.toLowerCase().includes(searchQuery.toLowerCase())) ||
    (lead.first_name && lead.first_name.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  const handleStatusChange = async (id: string, status: Lead['status']) => {
    try {
      await updateMutation.mutateAsync({ id, data: { status } });
    } catch (error) {
      console.error('Failed to update status:', error);
    }
  };

  const handleDelete = async (id: string) => {
    if (confirm('Bu lead\'i silmek istediğinize emin misiniz?')) {
      try {
        await deleteMutation.mutateAsync(id);
      } catch (error) {
        console.error('Failed to delete lead:', error);
      }
    }
  };

  const handleExport = () => {
    generateCSV(displayLeads, 'leads');
  };

  const COLORS = ['#3b82f6', '#8b5cf6', '#6366f1', '#10b981', '#ef4444'];
  const funnelData = Object.entries(displayFunnel).map(([name, value]) => ({ name, value }));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold">Lead'ler</h2>
          <p className="text-muted-foreground">Potansiyel müşterilerinizi yönetin</p>
        </div>
        <Button onClick={handleExport}>
          <Download className="h-4 w-4 mr-2" />
          CSV İndir
        </Button>
      </div>

      {/* Funnel Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle>Lead Hunisi</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[250px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={funnelData}
                    cx="50%"
                    cy="50%"
                    innerRadius={40}
                    outerRadius={80}
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

        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Durum Bazlı Dağılım</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              {Object.entries(displayFunnel).map(([status, count]) => (
                <div key={status} className="text-center p-4 bg-gray-50 rounded-lg">
                  <p className="text-2xl font-bold">{count}</p>
                  <Badge className={`mt-2 ${getStatusColor(status)}`}>
                    {status === 'new' ? 'Yeni' :
                     status === 'contacted' ? 'İletişime Geçildi' :
                     status === 'engaged' ? 'Etkileşimde' :
                     status === 'converted' ? 'Dönüştürüldü' : 'Kaybedildi'}
                  </Badge>
                </div>
              ))}
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
                placeholder="Lead ara..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9"
              />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-full sm:w-48">
                <SelectValue placeholder="Durum" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tümü</SelectItem>
                <SelectItem value="new">Yeni</SelectItem>
                <SelectItem value="contacted">İletişime Geçildi</SelectItem>
                <SelectItem value="engaged">Etkileşimde</SelectItem>
                <SelectItem value="converted">Dönüştürüldü</SelectItem>
                <SelectItem value="lost">Kaybedildi</SelectItem>
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
                  <TableHead>Lead</TableHead>
                  <TableHead>Kaynak</TableHead>
                  <TableHead>Durum</TableHead>
                  <TableHead>Skor</TableHead>
                  <TableHead>Tarih</TableHead>
                  <TableHead className="text-right">İşlemler</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredLeads.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center py-8 text-muted-foreground">
                      Lead bulunamadı
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredLeads.map((lead) => (
                    <TableRow key={lead.id}>
                      <TableCell>
                        <div>
                          <p className="font-medium">{lead.first_name || 'Anonim'}</p>
                          <p className="text-sm text-muted-foreground">@{lead.username || 'N/A'}</p>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline">{lead.source_group_title || 'Bilinmiyor'}</Badge>
                      </TableCell>
                      <TableCell>
                        <Select
                          value={lead.status}
                          onValueChange={(value) => handleStatusChange(lead.id, value as Lead['status'])}
                        >
                          <SelectTrigger className="w-32">
                            <Badge className={getStatusColor(lead.status)}>
                              {lead.status === 'new' ? 'Yeni' :
                               lead.status === 'contacted' ? 'İletişimde' :
                               lead.status === 'engaged' ? 'Etkileşim' :
                               lead.status === 'converted' ? 'Dönüştü' : 'Kaybıp'}
                            </Badge>
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="new">Yeni</SelectItem>
                            <SelectItem value="contacted">İletişime Geçildi</SelectItem>
                            <SelectItem value="engaged">Etkileşimde</SelectItem>
                            <SelectItem value="converted">Dönüştürüldü</SelectItem>
                            <SelectItem value="lost">Kaybedildi</SelectItem>
                          </SelectContent>
                        </Select>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <div className={`h-2 w-16 rounded-full bg-gray-200`}>
                            <div
                              className={`h-2 rounded-full ${
                                lead.score >= 80 ? 'bg-green-500' :
                                lead.score >= 50 ? 'bg-yellow-500' : 'bg-red-500'
                              }`}
                              style={{ width: `${lead.score}%` }}
                            />
                          </div>
                          <span className="text-sm font-medium">{lead.score}</span>
                        </div>
                      </TableCell>
                      <TableCell className="text-sm text-muted-foreground">
                        {formatRelativeTime(lead.created_at)}
                      </TableCell>
                      <TableCell className="text-right">
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="icon">
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem onClick={() => setSelectedLead(lead)}>
                              <Eye className="h-4 w-4 mr-2" /> Detay
                            </DropdownMenuItem>
                            <DropdownMenuItem>
                              <MessageCircle className="h-4 w-4 mr-2" /> DM Gönder
                            </DropdownMenuItem>
                            <DropdownMenuItem
                              className="text-red-600"
                              onClick={() => handleDelete(lead.id)}
                            >
                              <Trash2 className="h-4 w-4 mr-2" /> Sil
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

      {/* Lead Detail Modal */}
      <Dialog open={!!selectedLead} onOpenChange={() => setSelectedLead(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Lead Detayı</DialogTitle>
          </DialogHeader>
          {selectedLead && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">İsim</p>
                  <p className="font-medium">{selectedLead.first_name || 'Anonim'}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Kullanıcı Adı</p>
                  <p className="font-medium">@{selectedLead.username || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Kaynak Grup</p>
                  <p className="font-medium">{selectedLead.source_group_title || 'Bilinmiyor'}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Skor</p>
                  <p className="font-medium">{selectedLead.score}/100</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Durum</p>
                  <Badge className={getStatusColor(selectedLead.status)}>{selectedLead.status}</Badge>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Oluşturulma</p>
                  <p className="font-medium">{formatDate(selectedLead.created_at)}</p>
                </div>
              </div>
              {selectedLead.notes && (
                <div>
                  <p className="text-sm text-muted-foreground">Notlar</p>
                  <p className="mt-1">{selectedLead.notes}</p>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
