<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
 xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
 xmlns:str="http://exslt.org/strings"
 xmlns:func="http://exslt.org/functions"
 xmlns:grabber="localhost"
 extension-element-prefixes="str func">

 <xsl:decimal-format name="de" decimal-separator="," grouping-separator="." />

<func:function name="grabber:lower-case">
  <xsl:param name="str"/>
  <func:result select="translate($str, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
                                       'abcdefghijklmnopqrstuvwxyz')"/>
</func:function>

<func:function name="grabber:upper-case">
  <xsl:param name="str"/>
  <func:result select="translate($str, 'abcdefghijklmnopqrstuvwxyz',
                                       'ABCDEFGHIJKLMNOPQRSTUVWXYZ')"/>
</func:function>

<func:function name="grabber:ends-with">
  <xsl:param name="str"/>
  <xsl:param name="tail"/>

  <xsl:variable name="length" select="string-length($str)"/>
  <xsl:variable name="tailLength" select="string-length($tail)"/>
  <xsl:variable name="tailStart" select="$length - $tailLength + 1"/>
  <xsl:variable name="thetail" select="substring($str, $tailStart)"/>

  <func:result select="$thetail = $tail"/>
</func:function>

<func:function name="grabber:index-of">
  <xsl:param name="str" />
  <xsl:param name="tail" />

  <func:result select="string-length(substring-before($str, $tail))" />
</func:function>

<!--
Remove the given tail from the given string.
Does nothing if the given string does not end with the given tail.

@str:  The string from which the tail should be removed.
@tail: The tail that is removed from str.
@return: The string with the tail removed, or the original string.
-->
<func:function name="grabber:rstrip">
  <xsl:param name="str"/>
  <xsl:param name="tail"/>

  <xsl:variable name="length" select="string-length($str)"/>
  <xsl:variable name="tailLength" select="string-length($tail)"/>
  <xsl:variable name="tailStart" select="$length - $tailLength + 1"/>
  <xsl:variable name="thetail" select="substring($str, $tailStart)"/>

  <xsl:choose>
    <xsl:when test="$thetail = $tail">
      <func:result select="substring($str, 1, $tailStart - 1)"/>
    </xsl:when>
    <xsl:otherwise>
      <func:result select="$str"/>
    </xsl:otherwise>
  </xsl:choose>
</func:function>

<!--
Converts the given bandwidth string to an integer in kilobytes.

@bandwidth: The bandwidth as a string.
@return: The bandwidth in kilobytes.
-->
<func:function name="grabber:bw2int">
  <xsl:param name="bandwidth"/>
  <xsl:variable name="bw" select="grabber:rstrip(grabber:lower-case($bandwidth), 'bps')"/>
  <xsl:choose>
    <xsl:when test="not($bandwidth)
                 or $bandwidth = ''
                 or $bw = 'unknown'
                 or $bw = 'unlimited'">
      <func:result/>
    </xsl:when>
    <xsl:when test="$bw = 'e1'">
      <func:result select="2097152"/>
    </xsl:when>
    <xsl:when test="$bw = 'e3'">
      <func:result select="35192832"/>
    </xsl:when>
    <xsl:when test="starts-with($bw, 'oc')">
      <func:result select="substring($bw, 3) * 1024 * 52" />
    </xsl:when>
    <xsl:when test="grabber:ends-with($bw, 'k')">
      <func:result select="grabber:rstrip($bw, 'k')" />
    </xsl:when>
    <xsl:when test="grabber:ends-with($bw, 'm')">
      <func:result select="concat(grabber:rstrip($bw, 'm'), '000')" />
    </xsl:when>
    <xsl:when test="grabber:ends-with($bw, 'g')">
      <func:result select="concat(grabber:rstrip($bw, 'g'), '000000')" />
    </xsl:when>
    <xsl:otherwise>
      <func:result select="$bw div 1024"/>
    </xsl:otherwise>
  </xsl:choose>
</func:function>

<func:function name="grabber:fam2protocol">
  <xsl:param name="family" />
  <xsl:choose>
    <xsl:when test="$family = 'inet'">
      <func:result>ipv4</func:result>
    </xsl:when>
    <xsl:when test="$family = 'inet6'">
      <func:result>ipv6</func:result>
    </xsl:when>
    <xsl:otherwise>
      <func:result select="$family"/>
    </xsl:otherwise>
  </xsl:choose>
</func:function>



<func:function name="grabber:thsep">
  <xsl:param name="number" />
  <func:result>
    <xsl:value-of select="format-number($number, '#.###', 'de')" />
  </func:result>
</func:function>

<func:function name="grabber:netmask">
  <xsl:param name="pfxlen"/>
  <xsl:choose>
    <xsl:when test="$pfxlen = 32">
      <func:result>255.255.255.255</func:result>
    </xsl:when>
    <xsl:when test="$pfxlen = 31">
      <func:result>255.255.255.254</func:result>
    </xsl:when>
    <xsl:when test="$pfxlen = 30">
      <func:result>255.255.255.252</func:result>
    </xsl:when>
    <xsl:when test="$pfxlen = 29">
      <func:result>255.255.255.248</func:result>
    </xsl:when>
    <xsl:when test="$pfxlen = 28">
      <func:result>255.255.255.240</func:result>
    </xsl:when>
    <xsl:when test="$pfxlen = 27">
      <func:result>255.255.255.224</func:result>
    </xsl:when>
    <xsl:when test="$pfxlen = 26">
      <func:result>255.255.255.192</func:result>
    </xsl:when>
    <xsl:when test="$pfxlen = 25">
      <func:result>255.255.255.128</func:result>
    </xsl:when>
    <xsl:when test="$pfxlen = 24">
      <func:result>255.255.255.0</func:result>
    </xsl:when>
    <xsl:when test="$pfxlen = 24">
      <func:result>255.255.255.0</func:result>
    </xsl:when>
    <xsl:when test="$pfxlen = 23">
      <func:result>255.255.254.0</func:result>
    </xsl:when>
    <xsl:when test="$pfxlen = 22">
      <func:result>255.255.252.0</func:result>
    </xsl:when>
    <xsl:when test="$pfxlen = 21">
      <func:result>255.255.248.0</func:result>
    </xsl:when>
    <xsl:when test="$pfxlen = 20">
      <func:result>255.255.240.0</func:result>
    </xsl:when>
    <xsl:when test="$pfxlen = 19">
      <func:result>255.255.224.0</func:result>
    </xsl:when>
    <xsl:when test="$pfxlen = 18">
      <func:result>255.255.192.0</func:result>
    </xsl:when>
    <xsl:when test="$pfxlen = 17">
      <func:result>255.255.128.0</func:result>
    </xsl:when>
    <xsl:when test="$pfxlen = 16">
      <func:result>255.255.0.0</func:result>
    </xsl:when>
    <xsl:when test="$pfxlen = 15">
      <func:result>255.254.0.0</func:result>
    </xsl:when>
    <xsl:when test="$pfxlen = 14">
      <func:result>255.252.0.0</func:result>
    </xsl:when>
    <xsl:when test="$pfxlen = 13">
      <func:result>255.248.0.0</func:result>
    </xsl:when>
    <xsl:when test="$pfxlen = 12">
      <func:result>255.240.0.0</func:result>
    </xsl:when>
    <xsl:when test="$pfxlen = 11">
      <func:result>255.224.0.0</func:result>
    </xsl:when>
    <xsl:when test="$pfxlen = 10">
      <func:result>255.192.0.0</func:result>
    </xsl:when>
    <xsl:when test="$pfxlen = 9">
      <func:result>255.128.0.0</func:result>
    </xsl:when>
    <xsl:when test="$pfxlen = 8">
      <func:result>255.0.0.0</func:result>
    </xsl:when>
    <xsl:when test="$pfxlen = 7">
      <func:result>254.0.0.0</func:result>
    </xsl:when>
    <xsl:when test="$pfxlen = 6">
      <func:result>252.0.0.0</func:result>
    </xsl:when>
    <xsl:when test="$pfxlen = 5">
      <func:result>248.0.0.0</func:result>
    </xsl:when>
    <xsl:when test="$pfxlen = 4">
      <func:result>240.0.0.0</func:result>
    </xsl:when>
    <xsl:when test="$pfxlen = 3">
      <func:result>224.0.0.0</func:result>
    </xsl:when>
    <xsl:when test="$pfxlen = 2">
      <func:result>192.0.0.0</func:result>
    </xsl:when>
    <xsl:when test="$pfxlen = 1">
      <func:result>128.0.0.0</func:result>
    </xsl:when>
    <xsl:otherwise>
      <func:result>0.0.0.0</func:result>
    </xsl:otherwise>
  </xsl:choose>
</func:function>

</xsl:stylesheet>
