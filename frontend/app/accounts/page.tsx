'use client';

import React, { useState } from 'react';
import { Plus, Trash2, RefreshCw, UserCircle, CheckCircle, XCircle, AlertCircle, Smartphone } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Skeleton } from '@/components/ui/skeleton';
import { useAccounts, useDeleteAccount, useCheckAccountStatus } from '@/hooks/useAccounts';
import { AddAccountModal } from '@/components/accounts/AddAccountModal';
import { formatDate } from '@/lib/utils';
import { Account, AccountStatus } from '@/lib/types';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';

const getStatusBadge = (status: AccountStatus) => {
  const variants: Record<AccountStatus, { variant: 'default' | 'secondary' | 'destructive' | 'outline' | 'success' | 'warning'; icon: React.ReactNode; label: string }> = {
    active: { variant: 'success', icon: <CheckCircle className="h-3 w-3" />, label: 'Aktif' },
    inactive: { variant: 'secondary', icon: <AlertCircle className="h-3 w-3" />, label: 'Pasif' },
    banned: { variant: 'destructive', icon: <XCircle className="h-3 w-3" />, label: 'Banlı' },
    warming_up: { variant: 'warning', icon: <RefreshCw className="h-3 w-3" />, label: 'Isınma' },
  };
  
  const config = variants[status] || variants.inactive;
  
  return (
    <Badge variant={config.variant} className="gap-1">
      {config.icon}
      {config.label}
    </Badge>
  );
};

export default function AccountsPage() {
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [deleteAccountId, setDeleteAccountId] = useState<number | null>(null);
  const [checkingStatusId, setCheckingStatusId] = useState<number | null>(null);
  
  const { data: accounts, isLoading, refetch } = useAccounts();
  const deleteAccountMutation = useDeleteAccount();
  const checkStatusMutation = useCheckAccountStatus();

  const handleDelete = async () => {
    if (deleteAccountId !== null) {
      try {
        await deleteAccountMutation.mutateAsync(deleteAccountId);
        setDeleteAccountId(null);
      } catch (error) {
        console.error('Failed to delete account:', error);
      }
    }
  };

  const handleCheckStatus = async (id: number) => {
    setCheckingStatusId(id);
    try {
      await checkStatusMutation.mutateAsync(id);
    } catch (error) {
      console.error('Failed to check status:', error);
    } finally {
      setCheckingStatusId(null);
    }
  };

  const activeCount = accounts?.filter(a => a.status === 'active').length || 0;
  const totalCount = accounts?.length || 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold">Telegram Hesapları</h2>
          <p className="text-muted-foreground">Bağlı Telegram hesaplarınızı yönetin</p>
        </div>
        <Button onClick={() => setIsAddModalOpen(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Hesap Ekle
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Toplam Hesap</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalCount}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Aktif Hesap</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{activeCount}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Pasif/Banlı</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-500">{totalCount - activeCount}</div>
          </CardContent>
        </Card>
      </div>

      {/* Accounts Table */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle>Hesaplar</CardTitle>
            <Button variant="outline" size="sm" onClick={() => refetch()}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Yenile
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-3">
              {[...Array(3)].map((_, i) => (
                <Skeleton key={i} className="h-16 w-full" />
              ))}
            </div>
          ) : accounts && accounts.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Telefon</TableHead>
                  <TableHead>Kullanıcı Adı</TableHead>
                  <TableHead>Durum</TableHead>
                  <TableHead>Isınma Aşaması</TableHead>
                  <TableHead>Eklenme Tarihi</TableHead>
                  <TableHead className="text-right">İşlemler</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {accounts.map((account: Account) => (
                  <TableRow key={account.id}>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Smartphone className="h-4 w-4 text-gray-400" />
                        <span className="font-medium">{account.phone}</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      {account.username ? (
                        <span className="text-blue-600">@{account.username}</span>
                      ) : (
                        <span className="text-muted-foreground">-</span>
                      )}
                    </TableCell>
                    <TableCell>{getStatusBadge(account.status)}</TableCell>
                    <TableCell>
                      <Badge variant="outline">
                        Aşama {account.warmup_stage}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {formatDate(account.created_at)}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleCheckStatus(account.id)}
                          disabled={checkingStatusId === account.id}
                        >
                          {checkingStatusId === account.id ? (
                            <RefreshCw className="h-4 w-4 animate-spin" />
                          ) : (
                            <RefreshCw className="h-4 w-4" />
                          )}
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="text-red-600 hover:text-red-700 hover:bg-red-50"
                          onClick={() => setDeleteAccountId(account.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <div className="text-center py-12">
              <UserCircle className="h-12 w-12 mx-auto text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Henüz hesap eklenmemiş</h3>
              <p className="text-gray-500 mb-4">
                Başlamak için ilk Telegram hesabınızı ekleyin
              </p>
              <Button onClick={() => setIsAddModalOpen(true)}>
                <Plus className="h-4 w-4 mr-2" />
                İlk Hesabı Ekle
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Add Account Modal */}
      <AddAccountModal
        open={isAddModalOpen}
        onOpenChange={setIsAddModalOpen}
        onSuccess={() => refetch()}
      />

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteAccountId !== null} onOpenChange={() => setDeleteAccountId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Hesabı Sil</AlertDialogTitle>
            <AlertDialogDescription>
              Bu Telegram hesabını silmek istediğinize emin misiniz? Bu işlem geri alınamaz ve hesap Telegram'dan çıkış yapacaktır.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>İptal</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              className="bg-red-600 hover:bg-red-700"
            >
              {deleteAccountMutation.isPending ? 'Siliniyor...' : 'Sil'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
