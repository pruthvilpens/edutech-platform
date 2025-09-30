export default function Footer() {
  return (
    <footer className="mt-auto border-t bg-background/60 backdrop-blur">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex items-center justify-between">
          <div className="text-sm text-muted-foreground">
            © 2024 EduTech Platform
          </div>
          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            <span>Privacy</span>
            <span>Terms</span>
            <span>Support</span>
          </div>
        </div>
      </div>
    </footer>
  )
}