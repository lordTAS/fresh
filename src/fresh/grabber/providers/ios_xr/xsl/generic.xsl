<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
 xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
 xmlns:str="http://exslt.org/strings"
 xmlns:func="http://exslt.org/functions"
 xmlns:grabber="localhost"
 extension-element-prefixes="str func">
<xsl:import href="functions.xsl"/>
<xsl:import href="types.xsl"/>
<xsl:output method="xml" indent="yes" encoding="iso-8859-1" />

<xsl:variable name="shrun" select="xml"/>
<xsl:variable
 name="ver"
 select="document('show_version.xml', .)/xml"/>
<xsl:variable
 name="install-active"
 select="document('show_install_active_summary.xml', .)/xml"/>
<xsl:variable
 name="diag"
 select="document('admin_show_diag.xml', .)/xml"/>
<xsl:variable
 name="inv"
 select="document('admin_show_inventory.xml', .)/xml"/>
<xsl:variable
 name="shint"
 select="document('show_interface.xml', .)/xml"/>

<xsl:variable name="cards" select="$inv/element[@type != 'PORT' and @type != 'CHASSIS']"/>
<xsl:variable name="interfaces" select="$shint/interface"/>

<xsl:template match="element">
  <card>
    <!-- General card specific fields. -->
    <xsl:variable name="slotName" select="grabber:getSlotFromCard(.)"/>
    <xsl:attribute name="slot">
      <xsl:value-of select="$slotName"/>
    </xsl:attribute>
    <xsl:variable name="diagSlotName" select="grabber:getDiagSlotFromInv(.)"/>
    <xsl:variable name="diagSlot" select="$diag/card[@slot=$diagSlotName]"/>
    <name>
      <xsl:choose>
        <xsl:when test="$diagSlot/description">
          <xsl:value-of select="$diagSlot/description"/>
        </xsl:when>
        <xsl:when test="$diagSlot/main/partno">
            <xsl:value-of select="$diagSlot/main/partno"/>
        </xsl:when>
        <xsl:when test="$diagSlot/partno">
            <xsl:value-of select="$diagSlot/partno"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:text>unknown</xsl:text>
        </xsl:otherwise>
      </xsl:choose>
    </name>
    <type>
      <xsl:choose>
        <xsl:when test="$diagSlot/main/partno">
          <xsl:value-of select="$diagSlot/main/partno"/>
        </xsl:when>
        <xsl:when test="$diagSlot/pca/partno">
            <xsl:value-of select="$diagSlot/pca/partno"/>
        </xsl:when>
        <xsl:when test="$diagSlot/partno">
            <xsl:value-of select="$diagSlot/partno"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:text>unknown</xsl:text>
        </xsl:otherwise>
      </xsl:choose>
    </type>
    <part-number>
      <xsl:choose>
        <xsl:when test="$diagSlot/main/partno">
          <xsl:value-of select="$diagSlot/main/partno"/>
        </xsl:when>
        <xsl:when test="$diagSlot/pca/partno">
            <xsl:value-of select="$diagSlot/pca/partno"/>
        </xsl:when>
        <xsl:when test="$diagSlot/partno">
            <xsl:value-of select="$diagSlot/partno"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:text>unknown</xsl:text>
        </xsl:otherwise>
      </xsl:choose>
    </part-number>
    <serial-number>
      <xsl:value-of select="serialno"/>
    </serial-number>

    <!-- Submodules. -->
    <xsl:variable
        name="subslots"
        select="$cards[grabber:onSlot(., $slotName)]"/>
    <xsl:apply-templates select="$subslots"/>

    <!-- Physical interfaces on this card. -->
    <xsl:variable name="card" select="."/>
    <xsl:if test="not($subslots)">
      <xsl:for-each select="$interfaces">
        <xsl:variable name="physical"   select="grabber:getInterfaceName(@name)"/>
        <xsl:variable name="isphysical" select="grabber:isPhysicalInterface(@name)"/>
        <xsl:if test="$isphysical and grabber:interfaceIsOnSlot($card, .)">
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
    <configured-hostname>
      <xsl:value-of select="normalize-space(hostname)" />
    </configured-hostname>
    <configured-domain>
      <xsl:value-of select="normalize-space(domain)" />
    </configured-domain>
    <os>
      <system><xsl:text>IOS XR</xsl:text></system>
      <version><xsl:value-of select="normalize-space($ver/version)"/></version>
      <patches>
        <xsl:for-each select="$install-active//package">
          <package>
            <xsl:attribute name="name">
              <xsl:value-of select="@name"/>
            </xsl:attribute>
          </package>
        </xsl:for-each>
      </patches>
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
      select="$cards[contains(@name, '/RP0/*')]"/>
    <xsl:for-each select="$routeProcessors">
      <xsl:variable
        name="chassisNumber"
        select="grabber:getChassisNumberFromCard(.)"/>
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
          <xsl:apply-templates select="$cards[grabber:ends-with(@name, '/*')
                                       and
                                       grabber:onChassis(., $chassisNumber)]"/>
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
