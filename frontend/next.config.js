/** @type {import('next').NextConfig} */
const nextConfig = {
  typescript: {
    // Production build sırasında type hatalarını ignore et
    ignoreBuildErrors: true,
  },
  eslint: {
    // Production build sırasında ESLint hatalarını ignore et
    ignoreDuringBuilds: true,
  },
  output: 'standalone',
  // API URL'i environment variable'dan al
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
}

module.exports = nextConfig
