<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
 xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
 xmlns:str="http://exslt.org/strings"
 xmlns:func="http://exslt.org/functions"
 xmlns:grabber="localhost"
 extension-element-prefixes="str func">
<xsl:output method="xml" indent="yes" encoding="iso-8859-1" />

<xsl:variable name="ver" select="xml"/>
<xsl:variable
 name="chassis"
 select="document('show_chassis.xml', .)/xml"/>

<xsl:template match="card">
  <card>
    <!-- General card specific fields. -->
    <xsl:attribute name="slot">
      <xsl:value-of select="@slot"/>
    </xsl:attribute>
    <name>
      <xsl:value-of select="configured"/>
    </name>
    <type>
      <xsl:value-of select="installed"/>
    </type>
  </card>
</xsl:template>

<xsl:template match="/xml">
  <host
   xmlns=""
   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
   xsi:noNamespaceSchemaLocation="model.xsd">
    <!-- General host specific fields. -->
    <os>
      <system><xsl:text>SmartEdge OS</xsl:text></system>
      <version><xsl:value-of select="$ver/version"/></version>
    </os>
    <model>
      <xsl:value-of select="$chassis/platform"/>
    </model>

    <!-- Chassis. -->
    <chassis>
      <xsl:attribute name="name">
        <xsl:value-of select="$chassis/platform"/>
      </xsl:attribute>
      <os>
        <system><xsl:text>SmartEdge OS</xsl:text></system>
        <version><xsl:value-of select="$ver/version"/></version>
      </os>
      <model>
        <xsl:value-of select="$chassis/platform"/>
      </model>

      <equipment>
        <!-- Cards inserted directly into the chassis. -->
        <xsl:apply-templates select="$chassis/cards/card"/>
      </equipment>
    </chassis>
  </host>
</xsl:template>

</xsl:stylesheet>
