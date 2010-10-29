<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
 xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
 xmlns:str="http://exslt.org/strings"
 xmlns:func="http://exslt.org/functions"
 xmlns:cfggrab="localhost"
 extension-element-prefixes="str func">
<xsl:import href="../../../xsl/functions.xsl"/>

<func:function name="cfggrab:getInterfaceName">
  <xsl:param name="interfaceName"/>
  <func:result select="str:tokenize($interfaceName, '.:')[1]"/>
</func:function>

<func:function name="cfggrab:isPhysicalInterface">
  <xsl:param name="interfaceName"/>
  <xsl:variable
    name="physical"
    select="cfggrab:getInterfaceName($interfaceName)"/>

  <xsl:choose>
    <xsl:when test="starts-with(cfggrab:lower-case($interfaceName), 'vlan')
                 or starts-with(cfggrab:lower-case($interfaceName), 'lo')">
      <func:result select="false()"/>
    </xsl:when>

    <xsl:otherwise>
      <func:result select="$physical = $interfaceName"/>
    </xsl:otherwise>
  </xsl:choose>
</func:function>

<!--
Given a string, this function looks for the LAST occurence of
char in it, and crops string1 at that position. Examples:

  string, n = stri
  string, g = strin
  string, x = string
-->
<func:function name="cfggrab:cropAt">
  <xsl:param name="string"/>
  <xsl:param name="char"/>

  <xsl:choose>
    <xsl:when test="not(contains($string, $char))">
      <func:result select="$string"/>
    </xsl:when>

    <xsl:otherwise>
      <xsl:variable name="tail" select="str:tokenize($string, $char)[last()]"/>
      <func:result select="cfggrab:rstrip($string, $tail)"/>
    </xsl:otherwise>
  </xsl:choose>
</func:function>

<!--
Given an interface name (such as POS1/0, Loopback0, or POS2/0:0),
this function returns the position, e.g. 1/0, 0, or 2/0.
-->
<func:function name="cfggrab:getInterfacePosition">
  <xsl:param name="interfaceName"/>
  <xsl:variable
    name="position"
    select="str:tokenize($interfaceName, 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')[last()]"/>
  <xsl:variable
    name="type"
    select="cfggrab:rstrip($interfaceName, $position)"/>

  <xsl:choose>
    <!-- This happens when the given interface contained no type. -->
    <xsl:when test="contains($type, '/')">
      <func:result select="$interfaceName"/>
    </xsl:when>

    <!-- Interface names that have no '/' in them, such as 'Serial0'. -->
    <xsl:when test="not(contains($position, '/'))">
      <func:result select="$interfaceName"/>
    </xsl:when>

    <!-- Logical interface names. -->
    <xsl:when test="contains($position, '.')">
      <func:result select="cfggrab:cropAt($position, '.')"/>
    </xsl:when>

    <!-- Other logical interface names. -->
    <xsl:when test="contains($position, ':')">
      <func:result select="cfggrab:cropAt($position, ':')"/>
    </xsl:when>

    <!-- "Normal" interface names. -->
    <xsl:otherwise>
      <func:result select="$position"/>
    </xsl:otherwise>
  </xsl:choose>
</func:function>

<func:function name="cfggrab:getSlotNameFromCard">
  <xsl:param name="card"/>
  <xsl:variable name="slot">
    <xsl:for-each select="$card/ancestor-or-self::card | $card/ancestor-or-self::subslot">
      <xsl:sort select="count(ancestor::*)"
                data-type="number"
                order="ascending"/>
      <xsl:value-of select="@slot"/>
      <xsl:if test=". != $card">
        <xsl:text>/</xsl:text>
      </xsl:if>
    </xsl:for-each>
  </xsl:variable>
  <func:result select="$slot"/>
</func:function>

<func:function name="cfggrab:onSlot">
  <xsl:param name="card"/>
  <xsl:param name="interfaceName"/>
  <xsl:variable name="slot1" select="cfggrab:getSlotNameFromCard($card)"/>
  <xsl:variable name="slot2" select="cfggrab:getInterfacePosition($interfaceName)"/>
  <func:result select="$slot1 = $slot2 or starts-with($slot2, concat($slot1, '/'))"/>
</func:function>

<func:function name="cfggrab:onInterface">
  <xsl:param name="interfaceName"/>
  <xsl:param name="unitName"/>
  <func:result select="$interfaceName = cfggrab:getInterfaceName($unitName)"/>
</func:function>

</xsl:stylesheet>
