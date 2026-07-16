import Link from "next/link"

export default function HomePage() {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b">
        <div className="container flex h-14 items-center justify-between">
          <span className="font-bold text-lg">Resume Builder</span>
          <div className="flex items-center gap-2">
            <Link
              href="/login"
              className="text-sm text-muted-foreground hover:text-foreground transition-colors px-3 py-1.5"
            >
              Sign In
            </Link>
            <Link
              href="/register"
              className="text-sm bg-primary text-primary-foreground px-3 py-1.5 rounded-md hover:bg-primary/90 transition-colors"
            >
              Get Started
            </Link>
          </div>
        </div>
      </header>
      <main className="flex-1">
        <section className="py-20 md:py-32">
          <div className="container text-center">
            <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-4">
              AI-Powered Resume Builder
            </h1>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto mb-8">
              Create professional, ATS-friendly resumes with AI optimization. Import from LinkedIn,
              use custom templates, and tailor your resume for each job application.
            </p>
            <div className="flex justify-center gap-4">
              <Link
                href="/register"
                className="bg-primary text-primary-foreground px-6 py-3 rounded-md font-medium hover:bg-primary/90 transition-colors"
              >
                Create Your Resume
              </Link>
              <Link
                href="/login"
                className="bg-secondary text-secondary-foreground px-6 py-3 rounded-md font-medium hover:bg-secondary/80 transition-colors"
              >
                Sign In
              </Link>
            </div>
          </div>
        </section>
        <section className="py-16 bg-muted/50">
          <div className="container">
            <div className="grid md:grid-cols-3 gap-8">
              <div className="text-center">
                <h3 className="font-semibold text-lg mb-2">Import from LinkedIn</h3>
                <p className="text-sm text-muted-foreground">
                  Import your professional information from LinkedIn with a review step before saving.
                </p>
              </div>
              <div className="text-center">
                <h3 className="font-semibold text-lg mb-2">AI-Powered Optimization</h3>
                <p className="text-sm text-muted-foreground">
                  Get intelligent suggestions to tailor your resume for specific job descriptions.
                </p>
              </div>
              <div className="text-center">
                <h3 className="font-semibold text-lg mb-2">Multiple Export Formats</h3>
                <p className="text-sm text-muted-foreground">
                  Export to PDF, DOCX, HTML, or Markdown with professional templates.
                </p>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  )
}
