import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export function NewsSection() {
  const news = [
    {
      title: "AI-Powered Analysis Revolutionizes Business Intelligence",
      date: "June 15, 2023",
      description:
        "Learn how AI is transforming the way companies analyze their data.",
    },
    {
      title: "New Features Released for Enhanced Insights",
      date: "June 10, 2023",
      description:
        "Explore our latest features designed to provide deeper business insights.",
    },
    {
      title: "Customer Success Story: Global Tech Leader",
      date: "June 5, 2023",
      description:
        "See how a leading tech company improved their decision-making process.",
    },
  ];

  return (
    <section className="py-20">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold mb-4">
            Latest News
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Stay updated with the latest developments and success stories
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {news.map((item, index) => (
            <Card key={index} id={`rmd2ie_${index}`}>
              <CardContent className="pt-6" id={`pf85yw_${index}`}>
                <p
                  className="text-sm text-muted-foreground mb-2"
                  id={`3vm7ys_${index}`}
                >
                  {item.date}
                </p>
                <h3
                  className="text-xl font-semibold mb-2"
                  id={`a5x99f_${index}`}
                >
                  {item.title}
                </h3>
                <p
                  className="text-muted-foreground mb-4"
                  id={`q342wt_${index}`}
                >
                  {item.description}
                </p>
                <Button variant="link" className="px-0" id={`nba0nu_${index}`}>
                  Read More
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}
