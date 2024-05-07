/** @type {import('next').NextConfig} */

const nextConfig = {
  output: 'export',
  reactStrictMode: true,
  transpilePackages: [
    'antd', 
    '@ant-design', 
    '@ant-design/pro-chat',
    '@ant-design/pro-editor',
    'rc-util', 
    'rc-pagination', 
    'rc-picker', 
    'rc-tree', 
    'rc-table',
    'react-intersection-observer'
  ],
  eslint: {
    // Warning: This allows production builds to successfully complete even if
    // your project has ESLint errors.
    ignoreDuringBuilds: true,
  },
  basePath: '/boba',
  assetPrefix: '/boba',
  images: { unoptimized: true }
}

module.exports = nextConfig

