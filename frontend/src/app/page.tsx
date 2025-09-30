export default function Home() {
  return (
    <div className="min-h-screen bg-background">
      <main className="relative isolate">
        <section className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 py-20 sm:py-28">
          <div className="text-center">
            <h1 className="text-4xl sm:text-5xl font-semibold tracking-tight text-foreground">
              EduTech Platform
            </h1>
            <p className="mt-3 text-base sm:text-lg text-muted-foreground">
              AI-powered educational technology platform
            </p>
            <div className="mt-10 grid gap-2 text-sm text-muted-foreground justify-center">
              <p>🚀 Frontend: Running on port 3000</p>
              <p>🐍 Backend: Running on port 8000</p>
              <p>🗄️ Hasura: Running on port 8081</p>
              <p>🐘 PostgreSQL: Running on port 5432</p>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}