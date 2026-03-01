'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { Plus, Edit, Trash2, Eye, Bot, MessageSquare } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { usePersonas, useDeletePersona, usePreviewPersona } from '@/hooks/usePersonas';
import { Persona } from '@/lib/types';
import { Skeleton } from '@/components/ui/skeleton';

export default function PersonasPage() {
  const [selectedPersona, setSelectedPersona] = useState<Persona | null>(null);
  const [previewPrompt, setPreviewPrompt] = useState<string | null>(null);

  const { data: personas, isLoading } = usePersonas();
  const deleteMutation = useDeletePersona();
  const previewMutation = usePreviewPersona();

  // Mock data
  const mockPersonas: Persona[] = [
    {
      id: '1',
      name: 'Tech Enthusiast',
      bio: 'Teknoloji meraklısı, yazılım geliştirici. AI ve blockchain konularında tutkulu.',
      interests: ['teknoloji', 'yapıy zeka', 'blockchain', 'startup'],
      tone: 'friendly',
      sample_messages: ['Bu teknoloji gerçekten etkileyici!', 'AI ile neler yapılabilir düşünüyorum da...'],
      keywords_to_engage: ['ai', 'ml', 'startup', 'kod', 'python'],
      keywords_to_avoid: ['spam', 'reklam', 'satış'],
      is_active: true,
      created_at: '2026-01-15',
    },
    {
      id: '2',
      name: 'Crypto Trader',
      bio: 'Deneyimli kripto trader. DeFi ve NFT ekosisteminde aktif.',
      interests: ['bitcoin', 'ethereum', 'defi', 'nft', 'trading'],
      tone: 'professional',
      sample_messages: ['Piyasa görünümü ilginç geldi', 'Bu proje hakkında ne düşünüyorsunuz?'],
      keywords_to_engage: ['btc', 'eth', 'defi', 'yield', 'stake'],
      keywords_to_avoid: ['scam', 'pump', 'moonshot'],
      is_active: true,
      created_at: '2026-01-20',
    },
    {
      id: '3',
      name: 'Startup Founder',
      bio: 'Seri girişimci, SaaS ve B2B alanında tecrübeli.',
      interests: ['startup', 'saas', 'b2b', 'growth', 'marketing'],
      tone: 'casual',
      sample_messages: ['Girişimcilik yolculuğunda neler yaşıyorsunuz?', 'Büyüme stratejileri hakkında konuşmak isterim'],
      keywords_to_engage: ['startup', 'founder', 'mvp', 'investment', 'scale'],
      keywords_to_avoid: ['mlm', 'network marketing'],
      is_active: false,
      created_at: '2026-02-01',
    },
  ];

  const displayPersonas = personas || mockPersonas;

  const handleDelete = async (id: string) => {
    if (confirm('Bu personayı silmek istediğinize emin misiniz?')) {
      try {
        await deleteMutation.mutateAsync(id);
      } catch (error) {
        console.error('Failed to delete persona:', error);
      }
    }
  };

  const handlePreview = async (id: string) => {
    try {
      const result = await previewMutation.mutateAsync({ id });
      setPreviewPrompt(result.system_prompt);
    } catch (error) {
      console.error('Failed to preview persona:', error);
    }
  };

  const getToneLabel = (tone: string) => {
    const tones: Record<string, string> = {
      friendly: 'Samimi',
      professional: 'Profesyonel',
      casual: 'Rahat',
      formal: 'Resmi',
    };
    return tones[tone] || tone;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold">Personalar</h2>
          <p className="text-muted-foreground">Bot personalarını yönetin</p>
        </div>
        <Link href="/personas/new">
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Yeni Persona
          </Button>
        </Link>
      </div>

      {/* Persona Cards */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {Array(3).fill(0).map((_, i) => (
            <Card key={i}>
              <CardHeader>
                <Skeleton className="h-6 w-32" />
                <Skeleton className="h-4 w-full" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-20 w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {displayPersonas.map((persona) => (
            <Card key={persona.id} className={`relative ${!persona.is_active ? 'opacity-60' : ''}`}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                      <Bot className="h-5 w-5 text-blue-600" />
                    </div>
                    <div>
                      <CardTitle className="text-lg">{persona.name}</CardTitle>
                      <Badge variant={persona.is_active ? 'default' : 'secondary'}>
                        {persona.is_active ? 'Aktif' : 'Pasif'}
                      </Badge>
                    </div>
                  </div>
                </div>
                <CardDescription className="mt-2">{persona.bio}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Tone */}
                <div>
                  <p className="text-sm font-medium text-muted-foreground mb-1">Ton</p>
                  <Badge variant="outline">{getToneLabel(persona.tone)}</Badge>
                </div>

                {/* Interests */}
                <div>
                  <p className="text-sm font-medium text-muted-foreground mb-1">İlgi Alanları</p>
                  <div className="flex flex-wrap gap-1">
                    {persona.interests.slice(0, 4).map((interest, i) => (
                      <Badge key={i} variant="secondary" className="text-xs">
                        {interest}
                      </Badge>
                    ))}
                    {persona.interests.length > 4 && (
                      <Badge variant="secondary" className="text-xs">
                        +{persona.interests.length - 4}
                      </Badge>
                    )}
                  </div>
                </div>

                {/* Sample Message */}
                <div>
                  <p className="text-sm font-medium text-muted-foreground mb-1">Örnek Mesaj</p>
                  <div className="bg-gray-50 rounded-lg p-3">
                    <div className="flex items-start gap-2">
                      <MessageSquare className="h-4 w-4 text-muted-foreground mt-0.5" />
                      <p className="text-sm italic">"{persona.sample_messages[0]}"</p>
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex gap-2 pt-2">
                  <Button
                    variant="outline"
                    size="sm"
                    className="flex-1"
                    onClick={() => setSelectedPersona(persona)}
                  >
                    <Eye className="h-4 w-4 mr-1" /> Detay
                  </Button>
                  <Button variant="outline" size="sm">
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    className="text-red-600 hover:text-red-700"
                    onClick={() => handleDelete(persona.id)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Detail Modal */}
      <Dialog open={!!selectedPersona} onOpenChange={() => setSelectedPersona(null)}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>{selectedPersona?.name}</DialogTitle>
          </DialogHeader>
          {selectedPersona && (
            <div className="space-y-4">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Bio</p>
                <p>{selectedPersona.bio}</p>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Ton</p>
                  <Badge>{getToneLabel(selectedPersona.tone)}</Badge>
                </div>
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Durum</p>
                  <Badge variant={selectedPersona.is_active ? 'default' : 'secondary'}>
                    {selectedPersona.is_active ? 'Aktif' : 'Pasif'}
                  </Badge>
                </div>
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground mb-2">İlgi Alanları</p>
                <div className="flex flex-wrap gap-2">
                  {selectedPersona.interests.map((interest, i) => (
                    <Badge key={i} variant="secondary">{interest}</Badge>
                  ))}
                </div>
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground mb-2">Etkileşim Anahtar Kelimeleri</p>
                <div className="flex flex-wrap gap-2">
                  {selectedPersona.keywords_to_engage.map((kw, i) => (
                    <Badge key={i} variant="outline" className="bg-green-50">{kw}</Badge>
                  ))}
                </div>
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground mb-2">Kaçınılacak Kelimeler</p>
                <div className="flex flex-wrap gap-2">
                  {selectedPersona.keywords_to_avoid.map((kw, i) => (
                    <Badge key={i} variant="outline" className="bg-red-50">{kw}</Badge>
                  ))}
                </div>
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground mb-2">Örnek Mesajlar</p>
                <div className="space-y-2">
                  {selectedPersona.sample_messages.map((msg, i) => (
                    <div key={i} className="bg-gray-50 rounded-lg p-3">
                      <p className="text-sm italic">"{msg}"</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Preview Prompt Modal */}
      <Dialog open={!!previewPrompt} onOpenChange={() => setPreviewPrompt(null)}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>System Prompt Önizleme</DialogTitle>
          </DialogHeader>
          <div className="bg-gray-900 text-gray-100 rounded-lg p-4 max-h-96 overflow-auto">
            <pre className="text-sm whitespace-pre-wrap">{previewPrompt}</pre>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
