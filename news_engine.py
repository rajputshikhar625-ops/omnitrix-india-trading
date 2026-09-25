from datetime import datetime

from gnews import GNews


def fetch_news(
    symbol,
    max_results=20
):

    clean = (
        symbol
        .replace(".NS", "")
        .replace(".BO", "")
    )

    try:

        google_news = GNews(
            language="en",
            country="IN",
            period="7d",
            max_results=max_results
        )

        query = (
            f"{clean} stock India "
            f"company earnings "
            f"market news"
        )

        results = google_news.get_news(
            query
        )

        rows = []

        seen = set()

        for item in results:

            title = item.get(
                "title",
                ""
            ).strip()

            if not title:
                continue

            key = title.lower()

            if key in seen:
                continue

            seen.add(key)

            publisher = item.get(
                "publisher",
                {}
            )

            if isinstance(
                publisher,
                dict
            ):
                publisher = publisher.get(
                    "title",
                    "Unknown"
                )

            rows.append({
                "title": title,
                "publisher": publisher,
                "url": item.get(
                    "url",
                    ""
                ),
                "description": item.get(
                    "description",
                    ""
                ),
                "published": item.get(
                    "published date",
                    ""
                )
            })

        return rows

    except Exception as e:

        return [{
            "title": "NEWS ENGINE ERROR",
            "publisher": "System",
            "url": "",
            "description": str(e),
            "published": ""
        }]


def news_text(news):

    if not news:
        return "No news available."

    output = []

    for item in news:

        output.append(
            f"Headline: {item['title']}\n"
            f"Publisher: {item['publisher']}\n"
            f"Published: {item['published']}\n"
            f"Description: {item['description']}"
        )

    return "\n\n".join(
        output
    )
