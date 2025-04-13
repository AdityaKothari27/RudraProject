# {{user_name}}'s Personalized Newsletter

### {{date}}

## Today's Top Stories

{% for article in top_articles %}
### [{{article.title}}]({{article.url}})
{% if article.summary %}
{{article.summary}}
{% endif %}
*Source: {{article.source}}*

{% endfor %}

---

{% for category, articles in categorized_articles.items() %}
## {{category|capitalize}}

{% for article in articles %}
{% if article not in top_articles %}
### [{{article.title}}]({{article.url}})
{% if article.author %}
*By {{article.author}}*
{% endif %}
{% if article.summary %}
{{article.summary}}
{% endif %}
*Source: {{article.source}} | {{article.published_date|date_format}}*

{% endif %}
{% endfor %}

---

{% endfor %}

## Your Newsletter Preferences

Your newsletter is customized based on your interests:

**Interests:** {{interests|join(', ')}}

**Preferred Sources:** {{preferred_sources|join(', ')}}

*To update your preferences or unsubscribe, click [here](#).* 