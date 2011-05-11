<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
 xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
 xmlns:str="http://exslt.org/strings"
 xmlns:func="http://exslt.org/functions"
 xmlns:grabber="localhost"
 extension-element-prefixes="str func">

<xsl:template match="interface" mode="logical">
  <unit>
    <xsl:variable name="name" select="@name"/>
    <xsl:variable
      name="runint"
      select="$shrun/interface[@name=$name]"/>

    <!-- Interface attributes. -->
    <xsl:attribute name="name">
      <xsl:value-of select="@name" />
    </xsl:attribute>

    <!-- Interface description. -->
    <xsl:if test="description">
      <description>
        <xsl:value-of select="description"/>
      </description>
    </xsl:if>

    <!-- Interface bandwidth. -->
    <xsl:variable name="bw" select="grabber:bw2int(bw)" />
    <xsl:if test="$bw != ''">
      <bandwidth>
        <xsl:value-of select="$bw"/>
      </bandwidth>
    </xsl:if>

    <!-- IPv4 addresses. -->
    <xsl:variable
      name="addresses"
      select="$runint/ip-address | $runint/ipv4-address"/>
    <xsl:if test="$addresses/@address">
      <ipv4-address-list>
        <xsl:for-each select="$addresses">
          <xsl:if test="@address">
            <ipv4-address>
              <xsl:attribute name="address">
                <xsl:value-of select="@address" />
              </xsl:attribute>
              <xsl:attribute name="mask">
                <xsl:value-of select="@mask" />
              </xsl:attribute>
            </ipv4-address>
          </xsl:if>
        </xsl:for-each>
      </ipv4-address-list>
    </xsl:if>

    <!-- Service policy bindings. -->
    <xsl:for-each select="$runint/service-policy">
      <policy>
        <xsl:attribute name="direction">
          <xsl:value-of select="@direction" />
        </xsl:attribute>
        <xsl:value-of select="@name"/>
      </policy>
    </xsl:for-each>

    <!-- ISIS metric. -->
    <xsl:variable name="isis-ifc"
      select="$shrun//isis//interface[@name=$name] | $runint/isis" />
    <xsl:variable name="l1metric"
      select="$isis-ifc//metric[@level='1']" />
    <xsl:variable name="l2metric"
      select="$isis-ifc//metric[@level='2']" />
    <xsl:if test="$l1metric != ''">
      <isis-l1-metric>
        <xsl:value-of select="$l1metric"/>
      </isis-l1-metric>
    </xsl:if>
    <xsl:if test="$l2metric != ''">
      <isis-l2-metric>
        <xsl:value-of select="$l2metric"/>
      </isis-l2-metric>
    </xsl:if>

    <ipv4-statement>
      <!-- Sampling information. -->
      <xsl:for-each select="$runint/flow">
        <sampling>
          <xsl:attribute name="protocol">
              <xsl:value-of select="@protocol" />
          </xsl:attribute>
          <name>
              <xsl:value-of select="sampler" />
          </name>
          <direction>
              <xsl:value-of select="direction" />
          </direction>
        </sampling>
      </xsl:for-each>

      <!-- Service policy bindings. -->
      <xsl:for-each select="$runint/service-policy">
        <policy>
          <xsl:attribute name="direction">
            <xsl:value-of select="@direction" />
          </xsl:attribute>
          <xsl:value-of select="@name"/>
        </policy>
      </xsl:for-each>

      <!-- IPv4 addresses. -->
      <!--xsl:variable
        name="addresses"
        select="$runint/ip-address | $runint/ipv4-address"/-->
      <xsl:if test="$addresses/@address">
        <address-list>
          <xsl:for-each select="$addresses">
            <xsl:if test="@address">
              <ipv4-address>
                <xsl:attribute name="address">
                  <xsl:value-of select="@address" />
                </xsl:attribute>
                <xsl:attribute name="mask">
                  <xsl:value-of select="@mask" />
                </xsl:attribute>
              </ipv4-address>
            </xsl:if>
          </xsl:for-each>
        </address-list>
      </xsl:if>
    </ipv4-statement>
  </unit>
</xsl:template>

<xsl:template match="interface" mode="physical">
  <interface>
    <xsl:variable name="name" select="grabber:getInterfaceName(@name)"/>

    <!-- Interface attributes. -->
    <xsl:attribute name="name">
      <xsl:value-of select="$name" />
    </xsl:attribute>

    <!-- Interface description. -->
    <xsl:if test="description">
      <description>
        <xsl:value-of select="description"/>
      </description>
    </xsl:if>
 
    <!-- Interface bandwidth (kann nicht ermittelt werden - sh controller). -->

    <!-- Layer 2 protocol status. -->
    <l2-status>
      <xsl:choose>
        <xsl:when test="protocol = 'up' or starts-with(protocol, 'up ')">
          <xsl:text>active</xsl:text>
        </xsl:when>
        <xsl:when test="protocol = 'down' or starts-with(protocol, 'down ')">
          <xsl:text>inactive</xsl:text>
        </xsl:when>
        <xsl:when test="protocol = 'administratively down'">
          <xsl:text>inactive</xsl:text>
        </xsl:when>
        <!--
        Unfortunately, the parent controller of channelized interfaces
        does not show up in 'show interface', so in these cases we won't
        find any info on the status.
        TODO: Parse 'show controller' (or something else) to find the
        status.
        -->
        <xsl:when test="not(protocol) or protocol = 'not ready'">
          <xsl:text>unknown</xsl:text>
        </xsl:when>
      </xsl:choose>
    </l2-status>
  </interface>
</xsl:template>

</xsl:stylesheet>
