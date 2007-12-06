<?xml version="1.0"?>
<rss version="2.0">
   <channel>
      <title>Please log in to ${fc.req.config.site.name}</title>
      <link>${fc.url('home')}</link>
      <description>You need to log in to view this feed.</description>
      <generator>freeCritters</generator>
      <item>
         <title>Please log in to ${fc.config.site.name}</title>
         <link>${fc.url('login')|e}</link>
         <guid>${fc.url('login')|e}</guid>
      </item>
   </channel>
</rss>