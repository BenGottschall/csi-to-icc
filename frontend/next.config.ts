import type { NextConfig } from "next";

// Diagnostic: Check if environment variable is available during build
console.log('🔍 Build-time environment check:');
console.log('NEXT_PUBLIC_API_URL:', process.env.NEXT_PUBLIC_API_URL);
console.log('NODE_ENV:', process.env.NODE_ENV);

const nextConfig: NextConfig = {
  /* config options here */
  // Railway rebuild trigger
};

export default nextConfig;
