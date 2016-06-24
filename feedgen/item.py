# -*- coding: utf-8 -*-
"""
    feedgen.entry
    ~~~~~~~~~~~~~

    :copyright: 2013, Lars Kiesow <lkiesow@uos.de>

    :license: FreeBSD and LGPL, see license.* for more details.
"""
import collections

from lxml import etree
from datetime import datetime
import dateutil.parser
import dateutil.tz
from feedgen.util import ensure_format, formatRFC2822
from feedgen.compat import string_types


class BaseEpisode(object):
    """Class representing an episode in a podcast. Corresponds to an RSS Item.

    Its name indicates that this is the superclass for all episode classes.
    It is not meant to indicate that this class misses functionality; in 99%
    of all cases, this class is the right one to use for episodes.
    """

    def __init__(self):
        # RSS
        self.__rss_author      = None
        self.__rss_category    = None
        self.__rss_comments    = None
        self.__rss_description = None
        self.__rss_content     = None
        self.__rss_enclosure   = None
        self.__rss_guid        = None
        self.__rss_link        = None
        self.__rss_pubDate     = None
        self.__rss_source      = None
        self.__rss_title       = None

        # ITunes tags
        # http://www.apple.com/itunes/podcasts/specs.html#rss
        self.__itunes_author = None
        self.__itunes_block = None
        self.__itunes_image = None
        self.__itunes_duration = None
        self.__itunes_explicit = None
        self.__itunes_is_closed_captioned = None
        self.__itunes_order = None
        self.__itunes_subtitle = None
        self.__itunes_summary = None


    def rss_entry(self, extensions=True):
        """Create a RSS item and return it."""
        entry = etree.Element('item')
        if not ( self.__rss_title or self.__rss_description or self.__rss_content):
            raise ValueError('Required fields not set')
        if self.__rss_title:
            title = etree.SubElement(entry, 'title')
            title.text = self.__rss_title
        if self.__rss_link:
            link = etree.SubElement(entry, 'link')
            link.text = self.__rss_link
        if self.__rss_description and self.__rss_content:
            description = etree.SubElement(entry, 'description')
            description.text = self.__rss_description
            content = etree.SubElement(entry, '{%s}encoded' %
                                    'http://purl.org/rss/1.0/modules/content/')
            content.text = etree.CDATA(self.__rss_content['content']) \
                if self.__rss_content.get('type', '') == 'CDATA' else self.__rss_content['content']
        elif self.__rss_description:
            description = etree.SubElement(entry, 'description')
            description.text = self.__rss_description
        elif self.__rss_content:
            description = etree.SubElement(entry, 'description')
            description.text = self.__rss_content['content']
        for a in self.__rss_author or []:
            author = etree.SubElement(entry, 'author')
            author.text = a
        if self.__rss_guid:
            guid = etree.SubElement(entry, 'guid')
            guid.text = self.__rss_guid
            guid.attrib['isPermaLink'] = 'false'
        for cat in self.__rss_category or []:
            category = etree.SubElement(entry, 'category')
            category.text = cat['value']
            if cat.get('domain'):
                category.attrib['domain'] = cat['domain']
        if self.__rss_comments:
            comments = etree.SubElement(entry, 'comments')
            comments.text = self.__rss_comments
        if self.__rss_enclosure:
            enclosure = etree.SubElement(entry, 'enclosure')
            enclosure.attrib['url'] = self.__rss_enclosure['url']
            enclosure.attrib['length'] = self.__rss_enclosure['length']
            enclosure.attrib['type'] = self.__rss_enclosure['type']
        if self.__rss_pubDate:
            pubDate = etree.SubElement(entry, 'pubDate')
            pubDate.text = formatRFC2822(self.__rss_pubDate)

        # Itunes fields
        ITUNES_NS = 'http://www.itunes.com/dtds/podcast-1.0.dtd'

        if self.__itunes_author:
            author = etree.SubElement(entry, '{%s}author' % ITUNES_NS)
            author.text = self.__itunes_author

        if not self.__itunes_block is None:
            block = etree.SubElement(entry, '{%s}block' % ITUNES_NS)
            block.text = 'yes' if self.__itunes_block else 'no'

        if self.__itunes_image:
            image = etree.SubElement(entry, '{%s}image' % ITUNES_NS)
            image.attrib['href'] = self.__itunes_image

        if self.__itunes_duration:
            duration = etree.SubElement(entry, '{%s}duration' % ITUNES_NS)
            duration.text = self.__itunes_duration

        if self.__itunes_explicit in ('yes', 'no', 'clean'):
            explicit = etree.SubElement(entry, '{%s}explicit' % ITUNES_NS)
            explicit.text = self.__itunes_explicit

        if not self.__itunes_is_closed_captioned is None:
            is_closed_captioned = etree.SubElement(entry, '{%s}isClosedCaptioned' % ITUNES_NS)
            is_closed_captioned.text = 'yes' if self.__itunes_is_closed_captioned else 'no'

        if not self.__itunes_order is None and self.__itunes_order >= 0:
            order = etree.SubElement(entry, '{%s}order' % ITUNES_NS)
            order.text = str(self.__itunes_order)

        if self.__itunes_subtitle:
            subtitle = etree.SubElement(entry, '{%s}subtitle' % ITUNES_NS)
            subtitle.text = self.__itunes_subtitle

        if self.__itunes_summary:
            summary = etree.SubElement(entry, '{%s}summary' % ITUNES_NS)
            summary.text = self.__itunes_summary

        return entry



    def title(self, title=None):
        """Get or set the title value of the entry. It should contain a human
        readable title for the entry. Title is mandatory and should not be blank.

        :param title: The new title of the entry.
        :returns: The entriess title.
        """
        if not title is None:
            self.__rss_title = title
        return self.__rss_title


    def guid(self, guid=None):
        """Get or set the entries guid which is a string that uniquely identifies
        the item.

        :param guid: Id of the entry.
        :returns: Id of the entry.
        """
        if not guid is None:
            self.__rss_guid = guid
        return self.__rss_guid


    def author(self, author=None, replace=False, **kwargs):
        """Get or set autor data. An author element is a dict containing a name and
        an email adress. Email is mandatory.

        This method can be called with:
        - the fields of an author as keyword arguments
        - the fields of an author as a dictionary
        - a list of dictionaries containing the author fields

        An author has the following fields:
        - *name* conveys a human-readable name for the person.
        - *email* contains an email address for the person.

        :param author:  Dict or list of dicts with author data.
        :param replace: Add or replace old data.

        Example::

            >>> author( { 'name':'John Doe', 'email':'jdoe@example.com' } )
            [{'name':'John Doe','email':'jdoe@example.com'}]

            >>> author([{'name':'Mr. X'},{'name':'Max'}])
            [{'name':'John Doe','email':'jdoe@example.com'},
                    {'name':'John Doe'}, {'name':'Max'}]

            >>> author( name='John Doe', email='jdoe@example.com', replace=True )
            [{'name':'John Doe','email':'jdoe@example.com'}]

        """
        if author is None and kwargs:
            author = kwargs
        if not author is None:
            if replace or self.__rss_author is None:
                self.__rss_author = []
            authors = ensure_format( author,
                    set(['name', 'email']), set(['email']))
            self.__rss_author += ['%s (%s)' % ( a['email'], a['name'] ) for a in authors]
        return self.__rss_author


    def content(self, content=None, type=None):
        """Get or set the content of the entry which contains or links to the
        complete content of the entry. If the content is set (not linked) it will also set
        rss:description.

        :param content: The content of the feed entry.
        :param src: Link to the entries content.
        :param type: If type is CDATA content would not be escaped.
        :returns: Content element of the entry.
        """
        if not content is None:
            self.__rss_content = {'content':content}
            if not type is None:
                self.__rss_content['type'] = type
        return self.__rss_content


    def link(self, href=None):
        """Get or set the link to the full version of this episode description.

        :param href: the URI of the referenced resource (typically a Web page)
        :returns: The current link URI.
        """
        if not href is None:
            self.__rss_link = href
        return self.__rss_link


    def description(self, description=None):
        """Get or set the description value which is the item synopsis.

        :param description: Description of the entry.
        :returns: The entries description.
        """
        if not description is None:
            self.__rss_description = description
        return self.__rss_description

    def category(self, category=None, replace=False, **kwargs):
        """Get or set categories that the feed belongs to.

        This method can be called with:

        - the fields of a category as keyword arguments
        - the fields of a category as a dictionary
        - a list of dictionaries containing the category fields

        A categories has the following fields:

        - *term* identifies the category
        - *scheme* identifies the categorization scheme via a URI.

        If a label is present it is used for the RSS feeds. Otherwise the term is
        used. The scheme is used for the domain attribute in RSS.

        :param category:    Dict or list of dicts with data.
        :param replace: Add or replace old data.
        :returns: List of category data.
        """
        if category is None and kwargs:
            category = kwargs
        if not category is None:
            if replace or self.__rss_category is None:
                self.__rss_category = []
            if isinstance(category, collections.Mapping):
                category = [category]
            for cat in category:
                rss_cat = dict()
                rss_cat['value'] = cat['label'] if cat.get('label') else cat['term']
                if cat.get('scheme'):
                    rss_cat['domain'] = cat['scheme']
                self.__rss_category.append(rss_cat)
        return self.__rss_category


    def published(self, published=None):
        """Set or get the published value which contains the time of the initial
        creation or first availability of the entry.

        The value can either be a string which will automatically be parsed or a
        datetime.datetime object. In any case it is necessary that the value
        include timezone information.

        :param published: The creation date.
        :returns: Creation date as datetime.datetime
        """
        if not published is None:
            if isinstance(published, string_types):
                published = dateutil.parser.parse(published)
            if not isinstance(published, datetime):
                raise ValueError('Invalid datetime format')
            if published.tzinfo is None:
                raise ValueError('Datetime object has no timezone info')
            self.__rss_pubDate = published

        return self.__rss_pubDate


    def pubdate(self, pubDate=None):
        """Get or set the pubDate of the entry which indicates when the entry was
        published. This method is just another name for the published(...)
        method.
        """
        return self.published(pubDate)


    def comments(self, comments=None):
        """Get or set the the value of comments which is the url of the comments
        page for the item.

        :param comments: URL to the comments page.
        :returns: URL to the comments page.
        """
        if not comments is None:
            self.__rss_comments = comments
        return self.__rss_comments


    def enclosure(self, url=None, length=None, type=None):
        """Get or set the value of enclosure which describes a media object that
        is attached to this item.

        :param url: URL of the media object.
        :param length: Size of the media in bytes.
        :param type: Mimetype of the linked media.
        :returns: Data of the enclosure element.
        """
        if not url is None:
            self.__rss_enclosure = {'url': url, 'length': length, 'type': type}
        return self.__rss_enclosure

    def itunes_author(self, itunes_author=None):
        """Get or set the itunes:author of the podcast episode. The content of
        this tag is shown in the Artist column in iTunes. If the tag is not
        present, iTunes uses the contents of the <author> tag. If <itunes:author>
        is not present at the feed level, iTunes will use the contents of
        <managingEditor>.

        :param itunes_author: The author of the podcast.
        :type itunes_author: str
        :returns: The author of the podcast.
        """
        if not itunes_author is None:
            self.__itunes_author = itunes_author
        return self.__itunes_author

    def itunes_block(self, itunes_block=None):
        """Get or set the ITunes block attribute. Use this to prevent episodes
        from appearing in the iTunes podcast directory. Note that the episode can still be
        found by inspecting the XML, thus it is public.

        :param itunes_block: Block podcast episodes.
        :type itunes_block: bool
        :returns: If the podcast episode is blocked.
        """
        if not itunes_block is None:
            self.__itunes_block = itunes_block
        return self.__itunes_block

    def itunes_image(self, itunes_image=None):
        """Get or set the image for the podcast episode. This tag specifies the
        artwork for your podcast. Put the URL to the image in the href attribute.
        iTunes prefers square .jpg images that are at least 1400x1400 pixels,
        which is different from what is specified for the standard RSS image tag.
        In order for a podcast to be eligible for an iTunes Store feature, the
        accompanying image must be at least 1400x1400 pixels.

        iTunes supports images in JPEG and PNG formats with an RGB color space
        (CMYK is not supported). The URL must end in ".jpg" or ".png". If the
        <itunes:image> tag is not present, iTunes will use the contents of the
        RSS image tag.

        If you change your podcast’s image, also change the file’s name. iTunes
        may not change the image if it checks your feed and the image URL is the
        same. The server hosting your cover art image must allow HTTP head
        requests for iTS to be able to automatically update your cover art.

        :param itunes_image: Image of the podcast.
        :type itunes_image: str
        :returns: Image of the podcast.
        """
        if not itunes_image is None:
            lowercase_itunes_image = itunes_image.lower()
            if not (lowercase_itunes_image.endswith(('.jpg', '.jpeg', '.png'))):
                raise ValueError('Image filename must end with png or jpg, not .%s' % itunes_image.split(".")[-1])
            self.__itunes_image = itunes_image
        return self.__itunes_image

    def itunes_duration(self, itunes_duration=None):
        """Get or set the duration of the podcast episode. The content of this
        tag is shown in the Time column in iTunes.

        The tag can be formatted HH:MM:SS, H:MM:SS, MM:SS, or M:SS (H = hours,
        M = minutes, S = seconds). If an integer is provided (no colon present),
        the value is assumed to be in seconds. If one colon is present, the
        number to the left is assumed to be minutes, and the number to the right
        is assumed to be seconds. If more than two colons are present, the
        numbers farthest to the right are ignored.

        :param itunes_duration: Duration of the podcast episode.
        :type itunes_duration: str or int
        :returns: Duration of the podcast episode.
        """
        if not itunes_duration is None:
            itunes_duration = str(itunes_duration)
            if len(itunes_duration.split(':')) > 3 or \
                            itunes_duration.lstrip('0123456789:') != '':
                ValueError('Invalid duration format "%s"' % itunes_duration)
            self.__itunes_duration = itunes_duration
        return self.itunes_duration

    def itunes_explicit(self, itunes_explicit=None):
        """Get or the the itunes:explicit value of the podcast episode. This tag
        should be used to indicate whether your podcast episode contains explicit
        material. The three values for this tag are "yes", "no", and "clean".

        If you populate this tag with "yes", an "explicit" parental advisory
        graphic will appear next to your podcast artwork on the iTunes Store and
        in the Name column in iTunes. If the value is "clean", the parental
        advisory type is considered Clean, meaning that no explicit language or
        adult content is included anywhere in the episodes, and a "clean" graphic
        will appear. If the explicit tag is present and has any other value
        (e.g., "no"), you see no indicator — blank is the default advisory type.

        :param itunes_explicit: "yes" if the podcast contains explicit material, "clean" if it doesn't. "no" counts
            as blank.
        :type itunes_explicit: str
        :returns: If the podcast episode contains explicit material.
        """
        if not itunes_explicit is None:
            if not itunes_explicit in ('', 'yes', 'no', 'clean'):
                raise ValueError('Invalid value "%s" for explicit tag' % itunes_explicit)
            self.__itunes_explicit = itunes_explicit
        return self.__itunes_explicit

    def itunes_is_closed_captioned(self, itunes_is_closed_captioned=None):
        """Get or set the is_closed_captioned value of the podcast episode. This
        tag should be used if your podcast includes a video episode with embedded
        closed captioning support. The two values for this tag are "yes" and
        "no”.

        :param itunes_is_closed_captioned: If the episode has closed captioning support.
        :type itunes_is_closed_captioned: bool or str
        :returns: If the episode has closed captioning support.
        """
        if not itunes_is_closed_captioned is None:
            self.__itunes_is_closed_captioned = itunes_is_closed_captioned in ('yes', True)
        return self.__itunes_is_closed_captioned

    def itunes_order(self, itunes_order=None):
        """Get or set the itunes:order value of the podcast episode. This tag can
        be used to override the default ordering of episodes on the store.

        This tag is used at an <item> level by populating with the number value
        in which you would like the episode to appear on the store. For example,
        if you would like an <item> to appear as the first episode in the
        podcast, you would populate the <itunes:order> tag with “1”. If
        conflicting order values are present in multiple episodes, the store will
        use default ordering (pubDate).

        To remove the order from the episode set the order to a value below zero.

        :param itunes_order: The order of the episode.
        :type itunes_order: int
        :returns: The order of the episode.
        """
        if not itunes_order is None:
            self.__itunes_order = int(itunes_order)
        return self.__itunes_order

    def itunes_subtitle(self, itunes_subtitle=None):
        """Get or set the itunes:subtitle value for the podcast episode. The
        contents of this tag are shown in the Description column in iTunes. The
        subtitle displays best if it is only a few words long.

        :param itunes_subtitle: Subtitle of the podcast episode.
        :type itunes_subtitle: str
        :returns: Subtitle of the podcast episode.
        """
        if not itunes_subtitle is None:
            self.__itunes_subtitle = itunes_subtitle
        return self.__itunes_subtitle

    def itunes_summary(self, itunes_summary=None):
        """Get or set the itunes:summary value for the podcast episode. The
        contents of this tag are shown in a separate window that appears when the
        "circled i" in the Description column is clicked. It also appears on the
        iTunes page for your podcast. This field can be up to 4000 characters. If
        <itunes:summary> is not included, the contents of the <description> tag
        are used.

        :param itunes_summary: Summary of the podcast episode.
        :type itunes_summary: str
        :returns: Summary of the podcast episode.
        """
        if not itunes_summary is None:
            self.__itunes_summary = itunes_summary
        return self.__itunes_summary
