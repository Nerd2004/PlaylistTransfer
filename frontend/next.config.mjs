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
          {
            key: "Access-Control-Allow-Origin",
            value: "https://playlist-transfer-lovat.vercel.app", // Ensure the origin is correct
          },
          {
            key: "Access-Control-Allow-Headers",
            value: "Content-Type, Authorization",
          },
          {
            key: "Access-Control-Allow-Methods",
            value: "GET, POST, PUT, DELETE, OPTIONS",
          },
        ],
      },
    ];
  },
};
