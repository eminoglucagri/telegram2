'use client';

import React, { useState } from 'react';
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
import { useCreatePersona } from '@/hooks/usePersonas';

const personaSchema = z.object({
  name: z.string().min(2, 'Persona adı en az 2 karakter olmalı'),
  bio: z.string().min(10, 'Bio en az 10 karakter olmalı'),
  tone: z.string().min(1, 'Ton seçmelisiniz'),
  language_style: z.string().optional(),
});

type PersonaFormData = z.infer<typeof personaSchema>;

export default function NewPersonaPage() {
  const router = useRouter();
  const [interests, setInterests] = useState<string[]>([]);
  const [interestInput, setInterestInput] = useState('');
  const [engageKeywords, setEngageKeywords] = useState<string[]>([]);
  const [engageInput, setEngageInput] = useState('');
  const [avoidKeywords, setAvoidKeywords] = useState<string[]>([]);
  const [avoidInput, setAvoidInput] = useState('');
  const [sampleMessages, setSampleMessages] = useState<string[]>([]);
  const [sampleInput, setSampleInput] = useState('');

  const createMutation = useCreatePersona();

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<PersonaFormData>({
    resolver: zodResolver(personaSchema),
  });

  const addItem = (value: string, list: string[], setList: (v: string[]) => void, setInput: (v: string) => void) => {
    if (value.trim() && !list.includes(value.trim())) {
      setList([...list, value.trim()]);
      setInput('');
    }
  };

  const removeItem = (item: string, list: string[], setList: (v: string[]) => void) => {
    setList(list.filter(i => i !== item));
  };

  const onSubmit = async (data: PersonaFormData) => {
    if (interests.length === 0) {
      alert('En az bir ilgi alanı eklemelisiniz');
      return;
    }
    if (sampleMessages.length === 0) {
      alert('En az bir örnek mesaj eklemelisiniz');
      return;
    }

    try {
      await createMutation.mutateAsync({
        ...data,
        interests,
        keywords_to_engage: engageKeywords,
        keywords_to_avoid: avoidKeywords,
        sample_messages: sampleMessages,
      });
      router.push('/personas');
    } catch (error) {
      console.error('Failed to create persona:', error);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link href="/personas">
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-4 w-4" />
          </Button>
        </Link>
        <div>
          <h2 className="text-2xl font-bold">Yeni Persona</h2>
          <p className="text-muted-foreground">Yeni bir bot personası oluşturun</p>
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Basic Info */}
        <Card>
          <CardHeader>
            <CardTitle>Temel Bilgiler</CardTitle>
            <CardDescription>Persona adı, bio ve ton</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">Persona Adı *</Label>
              <Input
                id="name"
                placeholder="Örn: Tech Enthusiast"
                {...register('name')}
              />
              {errors.name && (
                <p className="text-sm text-red-500">{errors.name.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="bio">Bio *</Label>
              <Textarea
                id="bio"
                placeholder="Persona hakkında kısa bir açıklama..."
                {...register('bio')}
              />
              {errors.bio && (
                <p className="text-sm text-red-500">{errors.bio.message}</p>
              )}
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Ton *</Label>
                <Select onValueChange={(value) => setValue('tone', value)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Ton seçin" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="friendly">Samimi</SelectItem>
                    <SelectItem value="professional">Profesyonel</SelectItem>
                    <SelectItem value="casual">Rahat</SelectItem>
                    <SelectItem value="formal">Resmi</SelectItem>
                  </SelectContent>
                </Select>
                {errors.tone && (
                  <p className="text-sm text-red-500">{errors.tone.message}</p>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="language_style">Dil Stili</Label>
                <Input
                  id="language_style"
                  placeholder="Örn: Genç, emoji kullanır"
                  {...register('language_style')}
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Interests */}
        <Card>
          <CardHeader>
            <CardTitle>İlgi Alanları *</CardTitle>
            <CardDescription>Personanın ilgi duyduğu konular</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-2">
              <Input
                placeholder="İlgi alanı ekle..."
                value={interestInput}
                onChange={(e) => setInterestInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addItem(interestInput, interests, setInterests, setInterestInput))}
              />
              <Button type="button" onClick={() => addItem(interestInput, interests, setInterests, setInterestInput)}>
                <Plus className="h-4 w-4" />
              </Button>
            </div>
            <div className="flex flex-wrap gap-2">
              {interests.map((item, i) => (
                <Badge key={i} variant="secondary" className="flex items-center gap-1">
                  {item}
                  <button type="button" onClick={() => removeItem(item, interests, setInterests)} className="hover:text-red-500">
                    <X className="h-3 w-3" />
                  </button>
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Keywords */}
        <Card>
          <CardHeader>
            <CardTitle>Anahtar Kelimeler</CardTitle>
            <CardDescription>Etkileşim ve kaçınılacak kelimeler</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-4">
              <Label>Etkileşim Kelimeleri</Label>
              <div className="flex gap-2">
                <Input
                  placeholder="Anahtar kelime ekle..."
                  value={engageInput}
                  onChange={(e) => setEngageInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addItem(engageInput, engageKeywords, setEngageKeywords, setEngageInput))}
                />
                <Button type="button" onClick={() => addItem(engageInput, engageKeywords, setEngageKeywords, setEngageInput)}>
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
              <div className="flex flex-wrap gap-2">
                {engageKeywords.map((item, i) => (
                  <Badge key={i} className="bg-green-100 text-green-800 flex items-center gap-1">
                    {item}
                    <button type="button" onClick={() => removeItem(item, engageKeywords, setEngageKeywords)} className="hover:text-red-500">
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                ))}
              </div>
            </div>

            <div className="space-y-4">
              <Label>Kaçınılacak Kelimeler</Label>
              <div className="flex gap-2">
                <Input
                  placeholder="Kaçınılacak kelime ekle..."
                  value={avoidInput}
                  onChange={(e) => setAvoidInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addItem(avoidInput, avoidKeywords, setAvoidKeywords, setAvoidInput))}
                />
                <Button type="button" onClick={() => addItem(avoidInput, avoidKeywords, setAvoidKeywords, setAvoidInput)}>
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
              <div className="flex flex-wrap gap-2">
                {avoidKeywords.map((item, i) => (
                  <Badge key={i} className="bg-red-100 text-red-800 flex items-center gap-1">
                    {item}
                    <button type="button" onClick={() => removeItem(item, avoidKeywords, setAvoidKeywords)} className="hover:text-red-500">
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Sample Messages */}
        <Card>
          <CardHeader>
            <CardTitle>Örnek Mesajlar *</CardTitle>
            <CardDescription>Personanın kullanacağı örnek mesajlar</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-2">
              <Input
                placeholder="Örnek mesaj ekle..."
                value={sampleInput}
                onChange={(e) => setSampleInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addItem(sampleInput, sampleMessages, setSampleMessages, setSampleInput))}
              />
              <Button type="button" onClick={() => addItem(sampleInput, sampleMessages, setSampleMessages, setSampleInput)}>
                <Plus className="h-4 w-4" />
              </Button>
            </div>
            <div className="space-y-2">
              {sampleMessages.map((msg, i) => (
                <div key={i} className="flex items-center gap-2 p-3 bg-gray-50 rounded-lg">
                  <p className="flex-1 text-sm italic">"{msg}"</p>
                  <button type="button" onClick={() => removeItem(msg, sampleMessages, setSampleMessages)} className="text-red-500 hover:text-red-700">
                    <X className="h-4 w-4" />
                  </button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Actions */}
        <div className="flex justify-end gap-4">
          <Link href="/personas">
            <Button type="button" variant="outline">Vazgeç</Button>
          </Link>
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Oluşturuluyor...' : 'Persona Oluştur'}
          </Button>
        </div>
      </form>
    </div>
  );
}
