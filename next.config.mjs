/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // The local judge writes/compiles temp files and shells out to clang.
  // Keep server actions / route handlers on the Node.js runtime (default).
};

export default nextConfig;
