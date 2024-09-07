import Link from "next/link"

import { buttonVariants } from "@/components/ui/button"

export default function IndexPage() {
  return (
    <section className="container grid items-center gap-6 pb-8 pt-6 md:py-10">
      <div className="flex max-w-[980px] flex-col items-start gap-2">
        <h1 className="text-3xl font-extrabold leading-tight tracking-tighter md:text-4xl">
          Generate blog posts from publicly available code repositories
        </h1>
        <p className="max-w-[700px] text-lg text-muted-foreground">
          ByteBlogs parses and vectorizes code repositories to generate blog
          posts using AI. All you have do is provide a link to your code
          repository and details of your blog post, and we'll generate the rest.
        </p>
      </div>
      <div className="flex gap-4">
        <Link href="/generate" className={buttonVariants()}>
          Generate blog
        </Link>
      </div>
    </section>
  )
}
