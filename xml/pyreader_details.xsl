<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="2.0">
    <xsl:template match="DACC">
        <xsl:variable name="files" select="count(File)"/>
        <xsl:variable name="pass_count" select="count(File/Result[@status='pass'])"/>
        <xsl:variable name="fail_count" select="count(File/Result[@status='fail'])"/>
        <xsl:variable name="error_count" select="count(File/Result[@status='error'])"/>
        <html>
            <head>
                <style>
                    table, th, td {
                    border: 1px solid black;
                    border-collapse: collapse;
                    }
                    table {
                    border-bottom: 3px solid black;
                    }
                    th, td {
                    padding-top: 2px;
                    padding-bottom: 2px;
                    padding-left: 10px;
                    padding-right: 10px;
                    }
                    th, #ccid {
                    text-align: left;
                    }
                    td {
                    text-align: center;
                    }
                    .result-pass {
                    background-color: #ccffcc;
                    border-right: 3px solid black;
                    border-left: 3px solid black;
                    }
                    .result-fail {
                    background-color: #ffcccc;
                    border-right: 3px solid black;
                    border-left: 3px solid black;
                    }
                    .result-error {
                    background-color: #ffdab3;
                    border-right: 3px solid black;
                    border-left: 3px solid black;
                    }
                    .info {
                    border-right: 3px solid black;
                    border-left: 3px solid black;
                    }
                    .filename {
                    border-top: 3px solid black;
                    border-right: 3px solid black;
                    border-left: 3px solid black;
                    border-bottom: 3px dotted black;
                    }
                </style>
            </head>
            <body>
                <h1>S3-reader tests for  <xsl:value-of select="@name"/></h1>
                <xsl:value-of select="@date"/>
                <p>
                    Tested <xsl:value-of select="$files"/> Collections <br />
                    Passed: <xsl:value-of select="$pass_count"/> <br />
                    Failed: <xsl:value-of select="$fail_count"/> <br />
                    Errors: <xsl:value-of select="$error_count"/> <br />
                </p>
                <table>
                    <tr bgcolor="#9acd32">
                        <th class="filename" colspan="3" >Filename</th>
                    </tr>
                    <tr class="info" bgcolor="9acd32">
                        <th>Status</th>
                        <th>Code</th>
                        <th>Message</th>
                    </tr>
                    <xsl:apply-templates/>
                </table>
            </body>
        </html>
    </xsl:template>

    <xsl:template match="File">
        <tr title="{@url}" class="">
            <td class="filename" id="ccid" colspan="3" ><xsl:value-of select="@name"/></td>
        </tr>
	<xsl:apply-templates/>
    </xsl:template>
    
    <xsl:template match="Result">
        <tr class="result-{@status}">
            <td id="ccid" ><xsl:value-of select="@status"/></td>
            <td id="ccid" ><xsl:value-of select="@code"/></td>
            <td id="ccid" ><xsl:value-of select="@message"/></td>
        </tr>
    </xsl:template>
    
    <xsl:template match="Logs">
        <tr class="info">
            <td>Logs</td>
            <td colspan="2"><xsl:value-of select="@message"/></td>
        </tr>
    </xsl:template>
    
    <xsl:template match="Info">
        <tr class="info">
            <td>Info</td>
            <td colspan="2"><xsl:value-of select="@message"/></td>
        </tr>
    </xsl:template>
</xsl:stylesheet>
