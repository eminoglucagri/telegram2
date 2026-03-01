'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { ArrowLeft, Plus, X } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { useCreateCampaign } from '@/hooks/useCampaigns';
import { usePersonas } from '@/hooks/usePersonas';
import { Persona } from '@/lib/types';

const campaignSchema = z.object({
  name: z.string().min(3, 'Kampanya adı en az 3 karakter olmalı'),
  persona_id: z.string().min(1, 'Persona seçmelisiniz'),
  description: z.string().optional(),
  start_date: z.string().min(1, 'Başlangıç tarihi gerekli'),
  end_date: z.string().optional(),
});

type CampaignFormData = z.infer<typeof campaignSchema>;

export default function NewCampaignPage() {
  const router = useRouter();
  const [keywords, setKeywords] = React.useState<string[]>([]);
  const [keywordInput, setKeywordInput] = React.useState('');

  const { data: personas } = usePersonas(true);
  const createMutation = useCreateCampaign();

  const mockPersonas: Persona[] = [
    { id: '1', name: 'Tech Enthusiast', bio: 'Teknoloji meraklısı', interests: ['tech', 'ai'], tone: 'friendly', sample_messages: [], keywords_to_engage: [], keywords_to_avoid: [], is_active: true, created_at: '' },
    { id: '2', name: 'Crypto Trader', bio: 'Kripto trader', interests: ['crypto', 'defi'], tone: 'professional', sample_messages: [], keywords_to_engage: [], keywords_to_avoid: [], is_active: true, created_at: '' },
    { id: '3', name: 'Startup Founder', bio: 'Girişimci', interests: ['startup', 'saas'], tone: 'casual', sample_messages: [], keywords_to_engage: [], keywords_to_avoid: [], is_active: true, created_at: '' },
  ];

  const displayPersonas = personas || mockPersonas;

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<CampaignFormData>({
    resolver: zodResolver(campaignSchema),
    defaultValues: {
      start_date: new Date().toISOString().split('T')[0],
    },
  });

  const selectedPersonaId = watch('persona_id');
  const selectedPersona = displayPersonas.find(p => p.id === selectedPersonaId);

  const addKeyword = () => {
    if (keywordInput.trim() && !keywords.includes(keywordInput.trim())) {
      setKeywords([...keywords, keywordInput.trim()]);
      setKeywordInput('');
    }
  };

  const removeKeyword = (keyword: string) => {
    setKeywords(keywords.filter(k => k !== keyword));
  };

  const onSubmit = async (data: CampaignFormData) => {
    try {
      await createMutation.mutateAsync({
        ...data,
        target_keywords: keywords,
      });
      router.push('/campaigns');
    } catch (error) {
      console.error('Failed to create campaign:', error);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link href="/campaigns">
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-4 w-4" />
          </Button>
        </Link>
        <div>
          <h2 className="text-2xl font-bold">Yeni Kampanya</h2>
          <p className="text-muted-foreground">Yeni bir marketing kampanyası oluşturun</p>
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Basic Info */}
        <Card>
          <CardHeader>
            <CardTitle>Temel Bilgiler</CardTitle>
            <CardDescription>Kampanya adı ve açıklaması</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">Kampanya Adı *</Label>
              <Input
                id="name"
                placeholder="Örn: Kripto Topluluğu Kampanyası"
                {...register('name')}
              />
              {errors.name && (
                <p className="text-sm text-red-500">{errors.name.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Açıklama</Label>
              <Textarea
                id="description"
                placeholder="Kampanya hakkında kısa bir açıklama..."
                {...register('description')}
              />
            </div>
          </CardContent>
        </Card>

        {/* Persona Selection */}
        <Card>
          <CardHeader>
            <CardTitle>Persona Seçimi</CardTitle>
            <CardDescription>Kampanyada kullanılacak persona</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>Persona *</Label>
              <Select
                value={selectedPersonaId}
                onValueChange={(value) => setValue('persona_id', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Persona seçin" />
                </SelectTrigger>
                <SelectContent>
                  {displayPersonas.map((persona) => (
                    <SelectItem key={persona.id} value={persona.id}>
                      {persona.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {errors.persona_id && (
                <p className="text-sm text-red-500">{errors.persona_id.message}</p>
              )}
            </div>

            {selectedPersona && (
              <div className="bg-blue-50 rounded-lg p-4">
                <h4 className="font-medium text-blue-900">{selectedPersona.name}</h4>
                <p className="text-sm text-blue-700 mt-1">{selectedPersona.bio}</p>
                <div className="flex flex-wrap gap-1 mt-2">
                  {selectedPersona.interests.map((interest, i) => (
                    <Badge key={i} variant="secondary" className="text-xs">
                      {interest}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Keywords */}
        <Card>
          <CardHeader>
            <CardTitle>Hedef Anahtar Kelimeler</CardTitle>
            <CardDescription>Gruplarda aranacak kelimeler</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-2">
              <Input
                placeholder="Anahtar kelime ekle..."
                value={keywordInput}
                onChange={(e) => setKeywordInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addKeyword())}
              />
              <Button type="button" onClick={addKeyword}>
                <Plus className="h-4 w-4" />
              </Button>
            </div>
            <div className="flex flex-wrap gap-2">
              {keywords.map((keyword, i) => (
                <Badge key={i} variant="secondary" className="flex items-center gap-1">
                  {keyword}
                  <button
                    type="button"
                    onClick={() => removeKeyword(keyword)}
                    className="hover:text-red-500"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Dates */}
        <Card>
          <CardHeader>
            <CardTitle>Tarihler</CardTitle>
            <CardDescription>Kampanya başlangıç ve bitiş tarihleri</CardDescription>
          </CardHeader>
          <CardContent className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="start_date">Başlangıç Tarihi *</Label>
              <Input
                id="start_date"
                type="date"
                {...register('start_date')}
              />
              {errors.start_date && (
                <p className="text-sm text-red-500">{errors.start_date.message}</p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="end_date">Bitiş Tarihi</Label>
              <Input
                id="end_date"
                type="date"
                {...register('end_date')}
              />
            </div>
          </CardContent>
        </Card>

        {/* Actions */}
        <div className="flex justify-end gap-4">
          <Link href="/campaigns">
            <Button type="button" variant="outline">Vazgeç</Button>
          </Link>
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Oluşturuluyor...' : 'Kampanya Oluştur'}
          </Button>
        </div>
      </form>
    </div>
  );
}
