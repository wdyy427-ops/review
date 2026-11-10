param([Parameter(Mandatory=$true)][string]$InputPath,[Parameter(Mandatory=$true)][string]$OutputPath)
$ErrorActionPreference='Stop'
$word=$null
$doc=$null
try {
 $word=New-Object -ComObject Word.Application
 $word.Visible=$false
 $word.DisplayAlerts=0
 $doc=$word.Documents.Open($InputPath,$false,$true,$false)
 $doc.Repaginate()
 $pages=$doc.ComputeStatistics(2)
 $doc.ExportAsFixedFormat($OutputPath,17)
 Write-Output "Exported $pages pages to $OutputPath"
}
finally {
 if($null -ne $doc){$doc.Close(0);[void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($doc)}
 if($null -ne $word){$word.Quit();[void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($word)}
 [GC]::Collect()
 [GC]::WaitForPendingFinalizers()
}
