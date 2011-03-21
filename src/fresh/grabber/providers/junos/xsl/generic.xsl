<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
 xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
 xmlns:str="http://exslt.org/strings"
 xmlns:func="http://exslt.org/functions"
 xmlns:grabber="localhost"
 xmlns:ch="http://xml.juniper.net/junos/VERSION/junos-chassis"
 xmlns:shint="http://xml.juniper.net/junos/VERSION/junos-interface"
 extension-element-prefixes="str func"
 exclude-result-prefixes="ch">
<xsl:import href="functions.xsl"/>

<xsl:output method="xml" indent="yes" encoding="iso-8859-1" />
<xsl:variable
 name="ver"
 select="document('show_version.xml', .)/rpc-reply/software-information"/>
<xsl:variable
 name="multi-ver"
 select="document('show_version.xml', .)/rpc-reply/multi-routing-engine-results"/>
<xsl:variable
 name="first-ver"
 select="$ver | $multi-ver/multi-routing-engine-item[
            starts-with(re-name, 'scc-re') or starts-with(re-name, 'sfc')
         ][1]/software-information"/>
<xsl:variable
 name="ch"
 select="document('show_chassis_hardware.xml', .)/rpc-reply/ch:chassis-inventory/ch:chassis"/>
<xsl:variable
 name="multi-ch"
 select="document('show_chassis_hardware.xml', .)/rpc-reply/multi-routing-engine-results/multi-routing-engine-item"/>
<xsl:variable
 name="shint"
 select="document('show_interface.xml', .)/rpc-reply/shint:interface-information"/>

<xsl:variable name="nSlotsPerChassis" select="8"/>
<xsl:variable name="interfaces" select="$shint/shint:physical-interface"/>

<!-- Physical interfaces. -->
<xsl:template match="shint:physical-interface">
  <xsl:variable name="name" select="shint:name"/>
  <interface>
    <xsl:attribute name="name">
      <xsl:value-of select="$name" />
    </xsl:attribute>
    <xsl:if test="shint:description">
      <description>
        <xsl:value-of select="shint:description"/>
      </description>
    </xsl:if>

    <!-- Interface bandwidth. -->
    <xsl:variable name="bw" select="grabber:bw2int(shint:speed)" />
    <xsl:if test="$bw != ''">
      <bandwidth>
        <xsl:value-of select="$bw"/>
      </bandwidth>
    </xsl:if>

    <l2-status>
      <xsl:variable
        name="protocol"
        select="shint:oper-status"/>
      <xsl:choose>
        <xsl:when test="$protocol = 'up'">
          <xsl:text>active</xsl:text>
        </xsl:when>
        <xsl:when test="$protocol = 'down'">
          <xsl:text>inactive</xsl:text>
        </xsl:when>
      </xsl:choose>
    </l2-status>
  </interface>
</xsl:template>

<xsl:template match="ch:chassis-module | ch:chassis-sub-module">
  <card>
    <!-- General card specific fields. -->
    <xsl:variable name="slotName" select="grabber:getSlotNameFromCard(.)"/>
    <xsl:attribute name="slot">
      <xsl:value-of select="$slotName"/>
    </xsl:attribute>
    <name>
      <xsl:choose>
        <xsl:when test="ch:description != ''">
          <xsl:value-of select="ch:description"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:text>N/A</xsl:text>
        </xsl:otherwise>
      </xsl:choose>
    </name>
    <type>
      <xsl:choose>
        <xsl:when test="ch:model-number">
          <xsl:value-of select="ch:model-number"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:text>N/A</xsl:text>
        </xsl:otherwise>
      </xsl:choose>
    </type>
    <part-number>
      <xsl:value-of select="ch:part-number"/>
      <xsl:text> </xsl:text>
      <xsl:value-of select="ch:version"/>
    </part-number>
    <xsl:if test="ch:serial-number">
      <serial-number>
        <xsl:value-of select="ch:serial-number"/>
      </serial-number>
    </xsl:if>

    <!-- Submodules. -->
    <xsl:apply-templates select="ch:chassis-sub-module"/>

    <!-- Physical interfaces on this card. -->
    <xsl:if test="count(ch:chassis-sub-module) = 0">
      <xsl:variable name="card" select="."/>
      <xsl:apply-templates select="$interfaces[grabber:onSlot($card, $nSlotsPerChassis, shint:name)]"/>
    </xsl:if>
  </card>
</xsl:template>

<xsl:template match="/rpc-reply/configuration">
  <!--
  Collect a list of logical interfaces. Interfaces ending with ".32767" are
  internal interfaces created by JunOS automatically; we ignore them.
  -->
  <xsl:variable
    name="units"
    select="$interfaces/shint:logical-interface[shint:name and not(grabber:ends-with(shint:name, '.32767'))]"/>

  <host
   xmlns=""
   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
   xsi:noNamespaceSchemaLocation="model.xsd">
    <!-- General host specific fields. -->
    <configured-hostname>
      <xsl:value-of select="normalize-space($first-ver/host-name)" />
    </configured-hostname>
    <configured-domain>
      <xsl:value-of select="normalize-space(//system/domain-name)" />
    </configured-domain>
    <os>
      <system><xsl:text>JunOS</xsl:text></system>
      <version>
        <xsl:value-of select="substring-before(substring-after($first-ver/package-information[1]/comment, '['), ']')"/>
      </version>
    </os>
    <model>
      <xsl:value-of select="$first-ver/product-model"/>
    </model>

    <!-- Single chassis routers. -->
    <xsl:if test="$ch">
      <chassis>
        <xsl:attribute name="name">
          <xsl:value-of select="$ch/ch:name"/>
        </xsl:attribute>
        <os>
          <system><xsl:text>JunOS</xsl:text></system>
          <version>
            <xsl:value-of select="grabber:getJunOSVersionFromDescription($first-ver/package-information[1]/comment)"/>
          </version>
        </os>
        <model>
          <xsl:value-of select="$ch/ch:description"/>
        </model>

        <equipment>
          <xsl:apply-templates select="$ch/ch:chassis-module"/>
        </equipment>
      </chassis>
    </xsl:if>

    <!-- Multi chassis routers. -->
    <xsl:for-each select="$multi-ch">
      <chassis>
        <xsl:variable name="re-name" select="re-name"/>
        <xsl:variable name="sh-ver-re" select="$multi-ver/multi-routing-engine-item[re-name = $re-name]"/>
        <xsl:attribute name="name">
          <xsl:value-of select="$re-name"/>
        </xsl:attribute>
        <os>
          <system><xsl:text>JunOS</xsl:text></system>
          <version>
            <xsl:value-of select="grabber:getJunOSVersionFromDescription($sh-ver-re/software-information/package-information[1]/comment)"/>
          </version>
        </os>
        <model>
          <xsl:value-of select="$sh-ver-re/software-information/product-model"/>
        </model>

        <equipment>
          <xsl:apply-templates select="ch:chassis-inventory/ch:chassis/ch:chassis-module"/>
        </equipment>
      </chassis>
    </xsl:for-each>

    <!-- Logical interface units. -->
    <xsl:if test="$units">
      <unit-list>
        <xsl:for-each select="$units">
          <unit>
            <!-- Interface attributes. -->
            <xsl:attribute name="name">
              <xsl:value-of select="shint:name" />
            </xsl:attribute>

            <!-- Interface description. -->
            <description>
              <xsl:choose>
                <xsl:when test="shint:description">
                  <xsl:value-of select="shint:description"/>
                </xsl:when>
                <xsl:when test="../shint:description">
                  <xsl:value-of select="../shint:description"/>
                </xsl:when>
              </xsl:choose>
            </description>

            <!-- Interface bandwidth. -->
            <xsl:variable name="bw" select="grabber:bw2int(../shint:speed)" />
            <xsl:if test="$bw != ''">
              <bandwidth>
                <xsl:value-of select="$bw"/>
              </bandwidth>
            </xsl:if>

            <!-- IPv4 addresses. -->
            <xsl:variable
              name="addresses"
              select="shint:address-family[shint:address-family-name='inet']/shint:interface-address"/>
            <xsl:if test="$addresses">
              <ipv4-address-list>
                <xsl:for-each select="$addresses">
                  <ipv4-address>
                    <xsl:attribute name="address">
                      <xsl:value-of select="shint:ifa-local" />
                    </xsl:attribute>
                    <xsl:attribute name="mask">
                      <xsl:value-of select="grabber:netmask(str:tokenize(shint:ifa-destination, '/')[2])" />
                    </xsl:attribute>
                  </ipv4-address>
                </xsl:for-each>
              </ipv4-address-list>
            </xsl:if>

            <!-- Filter bindings. -->
            <xsl:variable
              name="filters"
              select="shint:family/shint:inet/shint:filter"/>
            <xsl:for-each select="$filters/shint:input">
              <policy direction="input">
                <xsl:value-of select="shint:filter-name"/>
              </policy>
            </xsl:for-each>
            <xsl:for-each select="$filters/shint:output">
              <policy direction="output">
                <xsl:value-of select="shint:filter-name"/>
              </policy>
            </xsl:for-each>
          </unit>
        </xsl:for-each>
      </unit-list>
    </xsl:if>
  </host>
</xsl:template>

</xsl:stylesheet>
