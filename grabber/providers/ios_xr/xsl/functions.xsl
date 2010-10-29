<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
 xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
 xmlns:str="http://exslt.org/strings"
 xmlns:func="http://exslt.org/functions"
 xmlns:grabber="localhost"
 extension-element-prefixes="str func">
<xsl:import href="../../ios/xsl/functions.xsl"/>

<func:function name="grabber:getChassisNumberFromCard">
  <xsl:param name="card"/>
  <func:result select="substring-before($card/@name, '/')"/>
</func:function>

<func:function name="grabber:getSlotFromCard">
  <xsl:param name="card"/>
  <xsl:variable name="slot1" select="grabber:rstrip($card/@name, '/CPU0')"/>
  <func:result select="grabber:rstrip($slot1, '/*')"/>
</func:function>

<func:function name="grabber:getDiagSlotFromInv">
  <xsl:param name="card"/>
  <func:result select="grabber:rstrip($card/@name, '/CPU0')"/>
</func:function>

<func:function name="grabber:onSlot">
  <xsl:param name="cardNode"/>
  <xsl:param name="slotName"/>

  <xsl:variable name="slot" select="grabber:getSlotFromCard($cardNode)"/>

  <func:result select="starts-with(concat($slot, '/'),
                                   concat($slotName, '/'))
                       and
                       string-length($slot) > string-length($slotName)"/>
</func:function>

<func:function name="grabber:interfaceIsOnSlot">
  <xsl:param name="cardNode"/>
  <xsl:param name="interfaceNode"/>

  <xsl:variable name="slot1" select="grabber:getSlotFromCard($cardNode)"/>
  <xsl:variable name="slot2" select="grabber:getInterfacePosition($interfaceNode/@name)"/>

  <func:result select="starts-with(concat($slot2, '/'), concat($slot1, '/'))"/>
</func:function>

<func:function name="grabber:onChassis">
  <xsl:param name="cardNode"/>
  <xsl:param name="chassisNumber"/>

  <xsl:variable name="slot" select="grabber:getChassisNumberFromCard($cardNode)"/>

  <func:result select="starts-with(concat($slot, '/'),
                                   concat($chassisNumber, '/'))"/>
</func:function>

</xsl:stylesheet>
