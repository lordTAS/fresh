<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
 xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
 xmlns:str="http://exslt.org/strings"
 xmlns:func="http://exslt.org/functions"
 xmlns:cfggrab="localhost"
 extension-element-prefixes="str func">
<xsl:import href="functions.xsl"/>
<xsl:import href="types.xsl"/>
<xsl:output method="xml" indent="yes" encoding="iso-8859-1" />

<xsl:variable name="shrun" select="xml"/>
<xsl:variable
 name="ver"
 select="document('show_version.xml', .)/xml"/>
<xsl:variable
 name="diag"
 select="document('admin_show_diag.xml', .)/xml"/>
<xsl:variable
 name="shint"
 select="document('show_interface.xml', .)/xml"/>

<xsl:variable name="cards" select="$diag/card[@type = 'CARD' or @type = 'SPA' or not(@type)]"/>
<xsl:variable name="interfaces" select="$shint/interface"/>

<xsl:template match="card">
  <card>
    <!-- General card specific fields. -->
    <xsl:variable name="slotName" select="cfggrab:getSlotFromCard(.)"/>
    <xsl:attribute name="slot">
      <xsl:value-of select="$slotName"/>
    </xsl:attribute>
    <name>
      <xsl:choose>
        <xsl:when test="description">
            <xsl:value-of select="description"/>
        </xsl:when>
        <xsl:when test="main/partno">
            <xsl:value-of select="main/partno"/>
        </xsl:when>
        <xsl:when test="partno">
            <xsl:value-of select="partno"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:text>unknown</xsl:text>
        </xsl:otherwise>
      </xsl:choose>
    </name>
    <type>
      <xsl:choose>
        <xsl:when test="main/partno">
            <xsl:value-of select="main/partno"/>
        </xsl:when>
        <xsl:when test="pca/partno">
            <xsl:value-of select="pca/partno"/>
        </xsl:when>
        <xsl:when test="partno">
            <xsl:value-of select="partno"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:text>unknown</xsl:text>
        </xsl:otherwise>
      </xsl:choose>
    </type>
    <xsl:if test="main">
      <part-number>
        <xsl:value-of select="main/partno"/>
      </part-number>
      <serial-number>
        <xsl:value-of select="main/serialno | pca/serialno"/>
      </serial-number>
    </xsl:if>

    <!-- Submodules. -->
    <xsl:variable
        name="subslots"
        select="$cards[cfggrab:onSlot(., $slotName)]"/>
    <xsl:apply-templates select="$subslots"/>

    <!-- Physical interfaces on this card. -->
    <xsl:variable name="card" select="."/>
    <xsl:if test="not($subslots)">
      <xsl:for-each select="$interfaces">
        <xsl:variable name="physical"   select="cfggrab:getInterfaceName(@name)"/>
        <xsl:variable name="isphysical" select="@name = $physical"/>
        <xsl:if test="$isphysical and cfggrab:interfaceIsOnSlot($card, .)">
          <xsl:apply-templates mode="physical" select="."/>
        </xsl:if>
      </xsl:for-each>
    </xsl:if>
  </card>
</xsl:template>

<xsl:template match="/xml">
  <host
   xmlns=""
   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
   xsi:noNamespaceSchemaLocation="model.xsd">
    <!-- General host specific fields. -->
    <xsl:attribute name="name">
      <xsl:value-of select="normalize-space(hostname)" />
    </xsl:attribute>
    <xsl:attribute name="domain">
      <xsl:value-of select="cfggrab:lower-case(normalize-space(domain))" />
    </xsl:attribute>
    <os>
      <system><xsl:text>IOS XR</xsl:text></system>
      <version><xsl:value-of select="normalize-space($ver/version)"/></version>
    </os>
    <model>
      <xsl:value-of select="$ver/model"/>
    </model>

    <!-- Single Chassis 12k. -->
    <xsl:if test="starts-with($ver/model, '12')">
      <chassis>
        <xsl:attribute name="name">
          <xsl:text>Chassis 0</xsl:text>
        </xsl:attribute>
        <os>
          <system><xsl:text>IOS XR</xsl:text></system>
          <version><xsl:value-of select="$ver/version"/></version>
        </os>
        <model>
          <xsl:value-of select="$ver/model"/>
        </model>

        <equipment>
          <xsl:apply-templates select="$cards[@type='CARD']"/>
        </equipment>
      </chassis>
    </xsl:if>

    <!-- Multi Chassis. -->
    <xsl:variable
      name="routeProcessors"
      select="$cards[contains(@slot, '/RP0/*')]"/>
    <xsl:for-each select="$routeProcessors">
      <xsl:variable
        name="chassisNumber"
        select="cfggrab:getChassisNumberFromCard(.)"/>
      <chassis>
        <xsl:attribute name="name">
            <xsl:text>Chassis </xsl:text>
            <xsl:value-of select="$chassisNumber"/>
        </xsl:attribute>
        <os>
          <system><xsl:text>IOS XR</xsl:text></system>
          <version><xsl:value-of select="$ver/version"/></version>
        </os>
        <model>
          <xsl:value-of select="$ver/model"/>
        </model>

        <equipment>
          <xsl:apply-templates select="$cards[cfggrab:ends-with(@slot, '/*')
                                       and
                                       cfggrab:onChassis(., $chassisNumber)]"/>
        </equipment>
      </chassis>
    </xsl:for-each>

    <!-- Logical interface units. -->
    <unit-list>
      <xsl:apply-templates select="$interfaces" mode="logical"/>
    </unit-list>
  </host>
</xsl:template>

</xsl:stylesheet>
