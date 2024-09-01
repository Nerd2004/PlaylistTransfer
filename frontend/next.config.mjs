import { createProxyMiddleware } from "http-proxy-middleware";

export default {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "https://playlist-transfer-backend.vercel.app/:path*", // Proxy to Backend
      },
    ];
  },
  async headers() {
    return [
      {
        source: "/api/:path*",
        headers: [
          {
            key: "Access-Control-Allow-Credentials",
            value: "true",
          },
        ],
      },
    ];
  },
  async redirects() {
    return [];
  },
};
