'use client';

import React, { useState, useEffect } from 'react';
import { Loader2, ArrowLeft, ArrowRight, Check, Shield, Phone, Key } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useInitiateLogin, useVerifyCode } from '@/hooks/useAccounts';

interface AddAccountModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess?: () => void;
}

type Step = 1 | 2 | 3;

export function AddAccountModal({ open, onOpenChange, onSuccess }: AddAccountModalProps) {
  const [step, setStep] = useState<Step>(1);
  const [apiId, setApiId] = useState('');
  const [apiHash, setApiHash] = useState('');
  const [phone, setPhone] = useState('');
  const [code, setCode] = useState('');
  const [password, setPassword] = useState('');
  const [phoneCodeHash, setPhoneCodeHash] = useState('');
  const [error, setError] = useState('');
  const [needs2FA, setNeeds2FA] = useState(false);

  const initiateLoginMutation = useInitiateLogin();
  const verifyCodeMutation = useVerifyCode();

  // Reset state when modal opens/closes
  useEffect(() => {
    if (!open) {
      setStep(1);
      setApiId('');
      setApiHash('');
      setPhone('');
      setCode('');
      setPassword('');
      setPhoneCodeHash('');
      setError('');
      setNeeds2FA(false);
    }
  }, [open]);

  const handleNext = () => {
    setError('');
    if (step === 1) {
      // Validate API credentials
      if (!apiId || !apiHash) {
        setError('API ID ve API Hash gereklidir');
        return;
      }
      if (isNaN(Number(apiId)) || Number(apiId) <= 0) {
        setError('API ID pozitif bir sayı olmalıdır');
        return;
      }
      setStep(2);
    }
  };

  const handleSendCode = async () => {
    setError('');
    if (!phone) {
      setError('Telefon numarası gereklidir');
      return;
    }
    
    // Validate phone format
    const cleanedPhone = phone.replace(/[\s\-()]/g, '');
    if (!cleanedPhone.match(/^\+?\d{10,15}$/)) {
      setError('Geçersiz telefon numarası formatı. Uluslararası format kullanın: +905xxxxxxxxx');
      return;
    }

    try {
      const result = await initiateLoginMutation.mutateAsync({
        api_id: Number(apiId),
        api_hash: apiHash,
        phone: cleanedPhone.startsWith('+') ? cleanedPhone : '+' + cleanedPhone,
      });
      setPhoneCodeHash(result.phone_code_hash);
      setStep(3);
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      setError(axiosError.response?.data?.detail || 'Doğrulama kodu gönderilemedi');
    }
  };

  const handleVerifyCode = async () => {
    setError('');
    if (!code || code.length < 4) {
      setError('Geçerli bir doğrulama kodu girin');
      return;
    }

    try {
      await verifyCodeMutation.mutateAsync({
        api_id: Number(apiId),
        api_hash: apiHash,
        phone: phone.startsWith('+') ? phone : '+' + phone,
        code: code,
        phone_code_hash: phoneCodeHash,
        password: needs2FA ? password : undefined,
      });
      onSuccess?.();
      onOpenChange(false);
    } catch (err: unknown) {
      const axiosError = err as { response?: { status?: number; data?: { detail?: string } } };
      if (axiosError.response?.status === 428) {
        // 2FA required
        setNeeds2FA(true);
        setError('İki faktörlü doğrulama etkin. Lütfen şifrenizi girin.');
      } else {
        setError(axiosError.response?.data?.detail || 'Doğrulama başarısız');
      }
    }
  };

  const handleBack = () => {
    setError('');
    if (step === 2) setStep(1);
    else if (step === 3) setStep(2);
  };

  const isLoading = initiateLoginMutation.isPending || verifyCodeMutation.isPending;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[450px]">
        <DialogHeader>
          <DialogTitle>Yeni Hesap Ekle</DialogTitle>
          <DialogDescription>
            Telegram hesabınızı bağlamak için aşağıdaki adımları izleyin
          </DialogDescription>
        </DialogHeader>

        {/* Progress indicator */}
        <div className="flex items-center justify-center gap-2 py-4">
          {[1, 2, 3].map((s) => (
            <div key={s} className="flex items-center">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                  step === s
                    ? 'bg-blue-600 text-white'
                    : step > s
                    ? 'bg-green-500 text-white'
                    : 'bg-gray-200 text-gray-600'
                }`}
              >
                {step > s ? <Check className="h-4 w-4" /> : s}
              </div>
              {s < 3 && (
                <div
                  className={`w-12 h-1 mx-1 ${
                    step > s ? 'bg-green-500' : 'bg-gray-200'
                  }`}
                />
              )}
            </div>
          ))}
        </div>

        {error && (
          <Alert variant="destructive" className="mb-4">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Step 1: API Credentials */}
        {step === 1 && (
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-sm text-muted-foreground mb-4">
              <Key className="h-4 w-4" />
              <span>
                API bilgilerinizi{' '}
                <a
                  href="https://my.telegram.org"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline"
                >
                  my.telegram.org
                </a>
                {' '}adresinden alabilirsiniz
              </span>
            </div>
            <div className="space-y-2">
              <Label htmlFor="api_id">API ID</Label>
              <Input
                id="api_id"
                type="number"
                placeholder="12345678"
                value={apiId}
                onChange={(e) => setApiId(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="api_hash">API Hash</Label>
              <Input
                id="api_hash"
                type="text"
                placeholder="0123456789abcdef0123456789abcdef"
                value={apiHash}
                onChange={(e) => setApiHash(e.target.value)}
              />
            </div>
          </div>
        )}

        {/* Step 2: Phone Number */}
        {step === 2 && (
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-sm text-muted-foreground mb-4">
              <Phone className="h-4 w-4" />
              <span>Telegram hesabınıza bağlı telefon numarasını girin</span>
            </div>
            <div className="space-y-2">
              <Label htmlFor="phone">Telefon Numarası</Label>
              <Input
                id="phone"
                type="tel"
                placeholder="+905551234567"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
              />
              <p className="text-xs text-muted-foreground">
                Uluslararası format kullanın: +905xxxxxxxxx
              </p>
            </div>
          </div>
        )}

        {/* Step 3: Verification Code */}
        {step === 3 && (
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-sm text-muted-foreground mb-4">
              <Shield className="h-4 w-4" />
              <span>Telegram uygulamanıza gönderilen kodu girin</span>
            </div>
            <div className="space-y-2">
              <Label htmlFor="code">Doğrulama Kodu</Label>
              <Input
                id="code"
                type="text"
                placeholder="12345"
                value={code}
                onChange={(e) => setCode(e.target.value.replace(/\D/g, ''))}
                maxLength={6}
              />
            </div>
            {needs2FA && (
              <div className="space-y-2">
                <Label htmlFor="password">İki Faktörlü Doğrulama Şifresi</Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
            )}
          </div>
        )}

        {/* Actions */}
        <div className="flex justify-between mt-6">
          {step > 1 ? (
            <Button variant="outline" onClick={handleBack} disabled={isLoading}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Geri
            </Button>
          ) : (
            <div />
          )}
          
          {step === 1 && (
            <Button onClick={handleNext}>
              İleri
              <ArrowRight className="h-4 w-4 ml-2" />
            </Button>
          )}
          
          {step === 2 && (
            <Button onClick={handleSendCode} disabled={isLoading}>
              {isLoading ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <ArrowRight className="h-4 w-4 mr-2" />
              )}
              Kod Gönder
            </Button>
          )}
          
          {step === 3 && (
            <Button onClick={handleVerifyCode} disabled={isLoading}>
              {isLoading ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <Check className="h-4 w-4 mr-2" />
              )}
              Doğrula ve Ekle
            </Button>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
