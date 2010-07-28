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

<func:function name="cfggrab:getInterfacePosition">
  <xsl:param name="interfaceName"/>
  <xsl:variable
    name="position"
    select="str:tokenize($interfaceName, 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')[last()]"/>
  <xsl:variable
    name="type"
    select="cfggrab:rstrip($interfaceName, $position)"/>

  <xsl:choose>
    <xsl:when test="contains($type, '/')">
      <func:result select="$interfaceName"/>
    </xsl:when>

    <xsl:when test="contains($position, '/')">
      <xsl:variable name="tail" select="str:tokenize($position, '/')[last()]"/>
      <func:result select="cfggrab:rstrip(cfggrab:rstrip($position, $tail), '/')"/>
    </xsl:when>

    <xsl:otherwise>
      <func:result select="$interfaceName"/>
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
  <func:result select="concat($slot1, '$') = concat($slot2, '$')"/>
</func:function>

<func:function name="cfggrab:onInterface">
  <xsl:param name="interfaceName"/>
  <xsl:param name="unitName"/>
  <func:result select="$interfaceName = cfggrab:getInterfaceName($unitName)"/>
</func:function>

</xsl:stylesheet>
