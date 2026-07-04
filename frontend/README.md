# Potato Shield Frontend

A modern, aesthetic frontend for the Potato Shield AI disease diagnosis system.

## Features

- 🥔 **3D Potato Animation** - Interactive 3D potato field using React Three Fiber
- 🤖 **Robotic Text Styling** - Pixelated, futuristic typography with orange glow effects
- 🔐 **Authentication** - User registration and login
- 💾 **Memory Visualization** - View and manage short-term and long-term memory
- 🎨 **Modern UI** - Black background with orange accents, smooth animations

## Tech Stack

- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **React Three Fiber** - 3D graphics
- **Framer Motion** - Animations
- **Tailwind CSS** - Styling
- **Axios** - API client

## Getting Started

1. Install dependencies:
```bash
npm install
```

2. Set environment variables:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

3. Run the development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000)

## Deployment to Vercel

1. Push your code to GitHub
2. Import your repository in Vercel
3. Set environment variable `NEXT_PUBLIC_API_URL` to your API URL
4. Deploy!

## Project Structure

```
frontend/
├── app/              # Next.js app directory
│   ├── dashboard/    # Main dashboard
│   ├── login/        # Login page
│   ├── register/     # Registration page
│   └── memory/       # Memory visualization
├── components/       # React components
│   ├── PotatoAnimation.tsx  # 3D potato animation
│   └── Layout.tsx    # Main layout
└── lib/              # Utilities
    └── api.ts        # API client
```

