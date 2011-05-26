<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
 xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
 xmlns:str="http://exslt.org/strings"
 xmlns:func="http://exslt.org/functions"
 xmlns:grabber="localhost"
 extension-element-prefixes="str func">
<xsl:import href="../../../xsl/functions.xsl"/>

<func:function name="grabber:getInterfaceName">
  <xsl:param name="interfaceName"/>
  <func:result select="str:tokenize($interfaceName, '.:')[1]"/>
</func:function>

<func:function name="grabber:isPhysicalInterface">
  <xsl:param name="interfaceName"/>
  <xsl:variable
    name="physical"
    select="grabber:getInterfaceName($interfaceName)"/>

  <xsl:choose>
    <xsl:when test="starts-with(grabber:lower-case($interfaceName), 'vlan')
                 or starts-with(grabber:lower-case($interfaceName), 'bundle')
                 or starts-with(grabber:lower-case($interfaceName), 'lo')">
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
<func:function name="grabber:cropAt">
  <xsl:param name="string"/>
  <xsl:param name="char"/>

  <xsl:choose>
    <xsl:when test="not(contains($string, $char))">
      <func:result select="$string"/>
    </xsl:when>

    <xsl:otherwise>
      <xsl:variable name="tail" select="str:tokenize($string, $char)[last()]"/>
      <func:result select="grabber:rstrip($string, $tail)"/>
    </xsl:otherwise>
  </xsl:choose>
</func:function>

<!--
Given an interface name (such as POS1/0, Loopback0, or POS2/0:0),
this function returns the position, e.g. 1/0, 0, or 2/0.
-->
<func:function name="grabber:getInterfacePosition">
  <xsl:param name="interfaceName"/>
  <xsl:variable
    name="position"
    select="str:tokenize($interfaceName, 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')[last()]"/>
  <xsl:variable
    name="type"
    select="grabber:rstrip($interfaceName, $position)"/>

  <xsl:choose>
    <!-- This happens when the given interface contained no type. -->
    <xsl:when test="contains($type, '/')">
      <func:result select="$interfaceName"/>
    </xsl:when>

    <!-- Logical interface names. -->
    <xsl:when test="contains($position, '.')">
      <func:result select="grabber:cropAt($position, '.')"/>
    </xsl:when>

    <!-- Other logical interface names. -->
    <xsl:when test="contains($position, ':')">
      <func:result select="grabber:cropAt($position, ':')"/>
    </xsl:when>

    <!-- "Normal" interface names. -->
    <xsl:otherwise>
      <func:result select="$position"/>
    </xsl:otherwise>
  </xsl:choose>
</func:function>

<func:function name="grabber:getSlotNameFromCard">
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

<func:function name="grabber:onSlot">
  <xsl:param name="card"/>
  <xsl:param name="interfaceName"/>
  <xsl:variable name="slot1" select="grabber:getSlotNameFromCard($card)"/>
  <xsl:variable name="slot2" select="grabber:getInterfacePosition($interfaceName)"/>
  <func:result select="str:tokenize($slot1, '-')[. = $slot2 or starts-with($slot2, concat(., '/'))]"/>
</func:function>

<func:function name="grabber:onInterface">
  <xsl:param name="interfaceName"/>
  <xsl:param name="unitName"/>
  <func:result select="$interfaceName = grabber:getInterfaceName($unitName)"/>
</func:function>

<func:function name="grabber:isDirection">
  <xsl:param name="direction"/>
  <xsl:choose>
    <xsl:when test="$direction = 'ingress'">
        <func:result>input</func:result>
    </xsl:when>
    <xsl:when test="$direction = 'egress'">
        <func:result>output</func:result>
    </xsl:when>
    <xsl:otherwise>
      <func:result select="$direction"/>
    </xsl:otherwise>
  </xsl:choose>
</func:function>

</xsl:stylesheet>
