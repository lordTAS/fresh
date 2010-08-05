<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
 xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
 xmlns:str="http://exslt.org/strings"
 xmlns:func="http://exslt.org/functions"
 xmlns:cfggrab="localhost"
 xmlns:ch="http://xml.juniper.net/junos/VERSION/junos-chassis"
 extension-element-prefixes="str func"
 exclude-result-prefixes="ch">
<xsl:import href="../../../xsl/functions.xsl"/>

<func:function name="cfggrab:getJunOSVersionFromDescription">
  <xsl:param name="description"/>
  <func:result select="substring-before(substring-after($description,  '['), ']')"/>
</func:function>

<!--
@interfaceName: A full interface name such as "so-0/0/1:0".
@return:        The FPC number.
-->
<func:function name="cfggrab:getAbsoluteFpcFromInterface">
  <xsl:param name="interfaceName"/>
  <xsl:choose>
    <xsl:when test="contains($interfaceName, '-')">
      <func:result select="str:tokenize(str:tokenize($interfaceName, '-')[2], '/')[1]"/>
    </xsl:when>
    <xsl:otherwise>
      <func:result select="''"/>
      <!-- func:result select="str:tokenize($interfaceName, 'abcdefghijklmnopqrstuvwxyz')[last()]"/ -->
    </xsl:otherwise>
  </xsl:choose>
</func:function>

<!--
@nSlotsPerChassis: The number of slots per chassis.
@interfaceName:    A full interface name such as "so-0/0/1:0".
@return:           The FPC number, relative to the first FPC in the same chassis.
-->
<func:function name="cfggrab:getRelativeFpcFromInterface">
  <xsl:param name="nSlotsPerChassis"/>
  <xsl:param name="interfaceName"/>
  <func:result select="cfggrab:getAbsoluteFpcFromInterface($interfaceName) mod $nSlotsPerChassis"/>
</func:function>

<!--
@interfaceName: A full interface name such as "so-0/0/1:0".
@return:        The PIC number.
-->
<func:function name="cfggrab:getPicFromInterface">
  <xsl:param name="interfaceName"/>
  <func:result select="str:tokenize(str:tokenize($interfaceName, '-')[2], '/')[2]"/>
</func:function>

<!--
@interfaceName: A full interface name such as "so-1/2/3:0".
@return:        The FPC and PIC slot such as "2/3".
-->
<func:function name="cfggrab:getAbsoluteSlotFromInterface">
  <xsl:param name="interfaceName"/>
  <func:result select="concat(cfggrab:getAbsoluteFpcFromInterface($interfaceName),
                              '/',
                              cfggrab:getPicFromInterface($interfaceName))"/>
</func:function>

<!--
@nSlotsPerChassis: The number of slots per chassis.
@interfaceName:    A full interface name such as "so-1/2/3:0".
@return:           The FPC and PIC slot, relative to the first FPC in the same chassis.
-->
<func:function name="cfggrab:getRelativeSlotFromInterface">
  <xsl:param name="nSlotsPerChassis"/>
  <xsl:param name="interfaceName"/>
  <func:result select="concat(cfggrab:getRelativeFpcFromInterface($nSlotsPerChassis, $interfaceName),
                              '/',
                              cfggrab:getPicFromInterface($interfaceName))"/>
</func:function>

<!--
@chassisNode: A chassis, chassis-module, or chassis-sub-module node.
@return:      The chassis number.
-->
<func:function name="cfggrab:getChassisNumberFromCard">
  <xsl:param name="chassisNode"/>
  <xsl:variable name="chassis" select="$chassisNode/ancestor-or-self::multi-routing-engine-item"/>
  <xsl:choose>
    <xsl:when test="$chassis/re-name">
      <func:result select="substring-after(substring-before($chassis/re-name, '-'), 'lcc')"/>
    </xsl:when>
    <xsl:otherwise>
      <func:result select="0"/>
    </xsl:otherwise>
  </xsl:choose>
</func:function>

<!--
@card:   A chassis-module, or chassis-sub-module node.
@return: The card number (not the card "path", just a single number).
-->
<func:function name="cfggrab:getCardNumberFromCard">
  <xsl:param name="card"/>
  <func:result select="str:tokenize($card/ch:name, ' ')[2]"/>
</func:function>

<!--
@card:   A chassis-module or chassis-sub-module node.
@return: A name such as "FPC 0/PIC 1".
-->
<func:function name="cfggrab:getSlotNameFromCard">
  <xsl:param name="card"/>
  <xsl:variable name="slot">
    <xsl:for-each select="$card/ancestor::ch:chassis-module | $card/ancestor::ch:chassis-sub-module">
      <xsl:sort select="count(ancestor::*)"
                data-type="number"
                order="ascending"/>
      <xsl:value-of select="ch:name"/>
      <xsl:text>/</xsl:text>
    </xsl:for-each>
    <xsl:value-of select="ch:name"/>
  </xsl:variable>
  <func:result select="$slot"/>
</func:function>

<!--
@card:             A chassis-module or chassis-sub-module node.
@nSlotsPerChassis: The number of slots per chassis.
@return:           A position of the card, such as "14/1".
-->
<func:function name="cfggrab:getAbsoluteSlotFromCard">
  <xsl:param name="card"/>
  <xsl:param name="nSlotsPerChassis"/>

  <xsl:variable name="chassisNumber" select="cfggrab:getChassisNumberFromCard($card)"/>
  <xsl:variable name="cardNumber" select="cfggrab:getCardNumberFromCard($card)"/>
  <xsl:variable name="offset" select="$nSlotsPerChassis * $chassisNumber"/>

  <xsl:choose>
    <xsl:when test="starts-with($card/ch:name, 'PIC ')">
      <func:result select="concat(cfggrab:getCardNumberFromCard($card/..) + $offset, '/', $cardNumber)"/>
    </xsl:when>
    <xsl:when test="starts-with($card/ch:name, 'FPC ')">
      <func:result select="$cardNumber + $offset"/>
    </xsl:when>
    <xsl:otherwise>
      <func:result select="''"/>
    </xsl:otherwise>
  </xsl:choose>
</func:function>

<func:function name="cfggrab:onSlot">
  <xsl:param name="card"/>
  <xsl:param name="nSlotsPerChassis"/>
  <xsl:param name="interfaceName"/>
  <xsl:variable name="slot1" select="cfggrab:getAbsoluteSlotFromCard($card, $nSlotsPerChassis)"/>
  <xsl:variable name="slot2" select="cfggrab:getAbsoluteSlotFromInterface($interfaceName)"/>
  <func:result select="starts-with(concat($slot1, '/'), concat($slot2, '/'))"/>
</func:function>

</xsl:stylesheet>
