import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  
  experimental: {
    serverActions: {
      bodySizeLimit: '25mb'
    }
  },
  
  async rewrites() {
    return [
      {
        // This rule is now specific to the telegram API
        source: '/api/telegram/:path*',
        destination: 'http://localhost:8000/api/telegram/:path*',
      },
    ];
  },
};

export default nextConfig;