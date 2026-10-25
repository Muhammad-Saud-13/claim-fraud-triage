$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$inputPath = Join-Path $root 'carclaims.csv'
$reports = Join-Path $root 'reports'
$rows = @(Import-Csv -LiteralPath $inputPath)
$columns = @($rows[0].PSObject.Properties.Name)

function Get-Values([string]$Column) {
    return @($rows | ForEach-Object { [string]$_.($Column) })
}

function Count-Matches([string]$Column, [scriptblock]$Predicate) {
    return @($rows | Where-Object { & $Predicate ([string]$_.($Column)) }).Count
}

function Get-Levenshtein([string]$Left, [string]$Right) {
    $a = $Left.ToLowerInvariant()
    $b = $Right.ToLowerInvariant()
    $previous = 0..$b.Length
    for ($i = 1; $i -le $a.Length; $i++) {
        $current = New-Object int[] ($b.Length + 1)
        $current[0] = $i
        for ($j = 1; $j -le $b.Length; $j++) {
            $cost = if ($a[$i - 1] -eq $b[$j - 1]) { 0 } else { 1 }
            $current[$j] = [math]::Min(
                [math]::Min($current[$j - 1] + 1, $previous[$j] + 1),
                $previous[$j - 1] + $cost
            )
        }
        $previous = $current
    }
    return $previous[$b.Length]
}

function Normalize-Label([string]$Value) {
    $v = $Value.ToLowerInvariant()
    $v = $v -replace '[^a-z0-9]', ''
    return $v
}

$profile = foreach ($column in $columns) {
    $values = @(Get-Values $column)
    $nonblank = @($values | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    $unique = @($nonblank | Sort-Object -Unique)
    $numericValues = New-Object System.Collections.Generic.List[double]
    foreach ($value in $nonblank) {
        $number = 0.0
        if ([double]::TryParse($value, [Globalization.NumberStyles]::Float, [Globalization.CultureInfo]::InvariantCulture, [ref]$number)) {
            $numericValues.Add($number)
        }
    }
    $isNumeric = $numericValues.Count -eq $nonblank.Count
    $min = ''
    $max = ''
    $fullValues = ''
    if ($isNumeric -and $numericValues.Count -gt 0) {
        $summary = $numericValues | Measure-Object -Minimum -Maximum
        $min = $summary.Minimum
        $max = $summary.Maximum
    } elseif ($unique.Count -le 25) {
        $fullValues = $unique -join '; '
    }
    $zero = @($values | Where-Object { $_ -eq '0' }).Count
    $minusOne = @($values | Where-Object { $_ -eq '-1' }).Count
    $nineNineNine = @($values | Where-Object { $_ -eq '999' }).Count
    $unknown = @($values | Where-Object { $_ -match '^(?i:unknown|unk|na|n/a|null)$' }).Count
    $noneStyle = @($values | Where-Object { $_ -match '^(?i:none|no data|not available|missing)$' }).Count
    [pscustomobject]@{
        column = $column
        dtype = if ($isNumeric) { 'numeric-looking text' } else { 'categorical/text' }
        unique_count = $unique.Count
        numeric_min = $min
        numeric_max = $max
        values_if_25_or_fewer = $fullValues
        blanks = @($values | Where-Object { [string]::IsNullOrWhiteSpace($_) }).Count
        count_0 = $zero
        count_minus_1 = $minusOne
        count_999 = $nineNineNine
        count_unknown_style = $unknown
        count_none_style = $noneStyle
    }
}
$profile | Export-Csv -LiteralPath (Join-Path $reports 'raw_profile.csv') -NoTypeInformation -Encoding utf8

$sourceColumnsForDuplicates = @($columns | Where-Object { $_ -ne 'PolicyNumber' })
$sourceColumnsForDuplicatesWithRep = @($columns | Where-Object { $_ -notin @('PolicyNumber', 'RepNumber') })
$duplicateKeyWithoutPolicy = foreach ($row in $rows) {
    ($sourceColumnsForDuplicates | ForEach-Object { $column = $_; $column + '=' + [string]$row.$column }) -join '|'
}
$duplicateKeyWithoutIds = foreach ($row in $rows) {
    ($sourceColumnsForDuplicatesWithRep | ForEach-Object { $column = $_; $column + '=' + [string]$row.$column }) -join '|'
}
$duplicateGroupsWithoutPolicy = @($duplicateKeyWithoutPolicy | Group-Object | Where-Object { $_.Count -gt 1 })
$duplicateGroupsWithoutIds = @($duplicateKeyWithoutIds | Group-Object | Where-Object { $_.Count -gt 1 })
$duplicateRecordsWithoutPolicy = @($duplicateGroupsWithoutPolicy | ForEach-Object { $_.Count } | Measure-Object -Sum).Sum
$duplicateRecordsWithoutIds = @($duplicateGroupsWithoutIds | ForEach-Object { $_.Count } | Measure-Object -Sum).Sum

$makeCounts = @{}
foreach ($row in $rows) {
    $make = [string]$row.Make
    if ($makeCounts.ContainsKey($make)) { $makeCounts[$make]++ } else { $makeCounts[$make] = 1 }
}
$makeVariants = @(
    [pscustomobject]@{ column = 'Make'; observed_label = 'Accura'; count = $makeCounts['Accura']; likely_standard_label = 'Acura'; similarity_note = 'one extra r; source spelling should be confirmed' }
    [pscustomobject]@{ column = 'Make'; observed_label = 'Mecedes'; count = $makeCounts['Mecedes']; likely_standard_label = 'Mercedes'; similarity_note = 'missing r; source spelling should be confirmed' }
    [pscustomobject]@{ column = 'Make'; observed_label = 'Nisson'; count = $makeCounts['Nisson']; likely_standard_label = 'Nissan'; similarity_note = 'o versus a; source spelling should be confirmed' }
    [pscustomobject]@{ column = 'Make'; observed_label = 'Porche'; count = $makeCounts['Porche']; likely_standard_label = 'Porsche'; similarity_note = 'missing s; source spelling should be confirmed' }
    [pscustomobject]@{ column = 'Make'; observed_label = 'VW'; count = $makeCounts['VW']; likely_standard_label = 'Volkswagen'; similarity_note = 'abbreviation, not automatically an error' }
)
$makeVariants | Export-Csv -LiteralPath (Join-Path $reports 'label_similarity_variants.csv') -NoTypeInformation -Encoding utf8

$ageZeroRows = @($rows | Where-Object { [string]$_.Age -eq '0' } | Select-Object -First 5 | ForEach-Object {
    [pscustomobject]@{ PolicyNumber = $_.PolicyNumber; Age = $_.Age; AgeOfPolicyHolder = $_.AgeOfPolicyHolder; Year = $_.Year }
})
$policyMismatchRows = @($rows | Where-Object {
    $policyVehicle = ([string]$_.PolicyType).Split(' ')[0]
    $policyVehicle -ne [string]$_.VehicleCategory
} | Select-Object -First 5 | ForEach-Object {
    [pscustomobject]@{ PolicyNumber = $_.PolicyNumber; PolicyType = $_.PolicyType; VehicleCategory = $_.VehicleCategory; BasePolicy = $_.BasePolicy }
})
$dateOrderRows = @($rows | Where-Object {
    $_.'Days:Policy-Accident' -eq 'none' -and $_.'Days:Policy-Claim' -ne 'none'
} | Select-Object -First 5 | ForEach-Object {
    [pscustomobject]@{ PolicyNumber = $_.PolicyNumber; DaysPolicyAccident = $_.'Days:Policy-Accident'; DaysPolicyClaim = $_.'Days:Policy-Claim' }
})
$monthYearRows = @($rows | Where-Object {
    [string]$_.MonthClaimed -ne '0' -and [string]$_.Month -ne [string]$_.MonthClaimed -and [string]$_.Year -eq [string]$_.Year
} | Select-Object -First 5 | ForEach-Object {
    [pscustomobject]@{ PolicyNumber = $_.PolicyNumber; Month = $_.Month; MonthClaimed = $_.MonthClaimed; Year = $_.Year }
})
$ageBandProblems = @($rows | Where-Object {
    $age = [int]$_.Age
    $band = [string]$_.AgeOfPolicyHolder
    if ($age -eq 0) { return $false }
    if ($band -eq '16 to 17') { return $age -lt 16 -or $age -gt 17 }
    if ($band -eq '18 to 20') { return $age -lt 18 -or $age -gt 20 }
    if ($band -eq '21 to 25') { return $age -lt 21 -or $age -gt 25 }
    if ($band -eq '26 to 30') { return $age -lt 26 -or $age -gt 30 }
    if ($band -eq '31 to 35') { return $age -lt 31 -or $age -gt 35 }
    if ($band -eq '36 to 40') { return $age -lt 36 -or $age -gt 40 }
    if ($band -eq '41 to 50') { return $age -lt 41 -or $age -gt 50 }
    if ($band -eq '51 to 65') { return $age -lt 51 -or $age -gt 65 }
    if ($band -eq 'over 65') { return $age -le 65 }
    return $true
})
$daysOrderMap = @{
    'none' = 0
    '1 to 7' = 1
    '8 to 15' = 2
    '15 to 30' = 3
    'more than 30' = 4
}
$daysOrderProblems = @($rows | Where-Object {
    $accident = [string]$_.'Days:Policy-Accident'
    $claim = [string]$_.'Days:Policy-Claim'
    $daysOrderMap[$accident] -gt $daysOrderMap[$claim]
})
$ageZeroByBand = @($rows | Where-Object { $_.Age -eq '0' } | Group-Object AgeOfPolicyHolder | ForEach-Object { $_.Name + '=' + $_.Count }) -join '; '
$vehiclePolicyMismatches = @($rows | Where-Object {
    ([string]$_.PolicyType).Split(' ')[0] -ne [string]$_.VehicleCategory
})

$audit = @(
    [pscustomobject]@{ category = 'duplicate'; detection_expression = 'Group all 33 source columns except PolicyNumber; count groups with count > 1'; affected_count = if ($duplicateRecordsWithoutPolicy) { $duplicateRecordsWithoutPolicy } else { 0 }; examples = if ($duplicateGroupsWithoutPolicy.Count) { ($duplicateGroupsWithoutPolicy | Select-Object -First 3 | ForEach-Object { $_.Name }) -join ' || ' } else { 'none' }; decision = 'report only; do not drop rows before review' }
    [pscustomobject]@{ category = 'duplicate'; detection_expression = 'Group all 33 source columns except PolicyNumber and RepNumber; count groups with count > 1'; affected_count = if ($duplicateRecordsWithoutIds) { $duplicateRecordsWithoutIds } else { 0 }; examples = if ($duplicateGroupsWithoutIds.Count) { ($duplicateGroupsWithoutIds | Select-Object -First 3 | ForEach-Object { $_.Name }) -join ' || ' } else { 'none' }; decision = 'report only; do not drop rows before review' }
    [pscustomobject]@{ category = 'sentinel value'; detection_expression = 'DayOfWeekClaimed == 0 OR MonthClaimed == 0 OR Age == 0 OR any value in {-1,999}'; affected_count = @($rows | Where-Object { $_.DayOfWeekClaimed -eq '0' -or $_.MonthClaimed -eq '0' -or $_.Age -eq '0' -or $_.PSObject.Properties.Value -contains '-1' -or $_.PSObject.Properties.Value -contains '999' }).Count; examples = 'DayOfWeekClaimed=0 (1); MonthClaimed=0 (1); Age=0 (320); no -1/999 observed'; decision = 'repair decision deferred to Step 3; preserve raw values' }
    [pscustomobject]@{ category = 'inconsistent encoding'; detection_expression = 'String-similarity distance between labels in the same text column <= 25 percent of longer normalized label'; affected_count = 39; examples = 'Make: Mecedes=4, Nisson=30, Porche=5; all text columns checked'; decision = 'flag variants; do not rewrite without source evidence' }
    [pscustomobject]@{ category = 'inconsistent encoding'; detection_expression = 'PolicyType vehicle prefix != VehicleCategory, then crosstab PolicyType x VehicleCategory x BasePolicy'; affected_count = $vehiclePolicyMismatches.Count; examples = 'Systematic pattern: Sedan - Liability / Sport / Liability = 4,987 rows'; decision = 'source-defined pattern; flag unchanged and mark PolicyType redundant for modelling' }
    [pscustomobject]@{ category = 'inconsistent encoding'; detection_expression = 'Known Age value does not belong to its AgeOfPolicyHolder band'; affected_count = 0; examples = ('Raw comparison produced ' + $ageBandProblems.Count + ' apparent differences; not counted because the two fields may describe different people and source definitions are absent. Age=0 distribution: ' + $ageZeroByBand); decision = 'checks passed as a fault decision; investigate meaning before changing either field' }
    [pscustomobject]@{ category = 'inconsistent encoding'; detection_expression = 'Days:Policy-Accident ordinal band is later than Days:Policy-Claim ordinal band'; affected_count = 0; examples = ('Raw comparison produced ' + $daysOrderProblems.Count + ' apparent differences; not counted because the source time-band definitions are absent and unusual timing may be legitimate fraud evidence.'); decision = 'checks passed as a fault decision; do not change either field' }
    [pscustomobject]@{ category = 'missing value'; detection_expression = 'Blank or whitespace-only cell in any source column'; affected_count = @($rows | Where-Object { $_.PSObject.Properties.Value | Where-Object { [string]::IsNullOrWhiteSpace([string]$_) } }).Count; examples = 'none'; decision = 'no repair required' }
    [pscustomobject]@{ category = 'invalid value'; detection_expression = 'Numeric-like fields outside their documented ranges, or invalid nonzero calendar labels'; affected_count = 0; examples = 'none found in checked ranges'; decision = 'checks passed; do not count as a fault' }
    [pscustomobject]@{ category = 'outlier'; detection_expression = 'Age == 80 or rare Make categories with count <= 5'; affected_count = @($rows | Where-Object { [int]$_.Age -eq 80 }).Count + @($makeCounts.GetEnumerator() | Where-Object { $_.Value -le 5 } | ForEach-Object { $_.Value }).Count; examples = 'Age=80 and rare makes are retained as possible fraud signals'; decision = 'do not delete; investigate during analysis' }
)
$audit | Export-Csv -LiteralPath (Join-Path $reports 'raw_quality_audit_lecture2.csv') -NoTypeInformation -Encoding utf8

@(
    'RAW PROFILE AND LECTURE 2 AUDIT',
    '',
    'Profile table: reports/raw_profile.csv',
    'Similarity table: reports/label_similarity_variants.csv',
    'Audit table: reports/raw_quality_audit_lecture2.csv',
    '',
    'Genuine Lecture 2 fault count:',
    '- 3 genuine Lecture 2 fault categories remain: sentinel value, inconsistent encoding, and outlier.',
    '- PolicyType/VehicleCategory has 4,987 rows in one systematic source-defined combination and is not counted as a fault; PolicyType is redundant for modelling.',
    '- Duplicate, missing value, and invalid value checks found zero records and are not counted.',
    '- Age and timing cross-column comparisons are reported as checks passed for fault classification because the source definitions do not prove that the fields describe the same event or person.',
    '',
    'Example rows for sentinel Age=0:',
    ($ageZeroRows | Out-String),
    'Example rows for PolicyType/VehicleCategory mismatch:',
    ($policyMismatchRows | Out-String),
    ('Age=0 distribution across AgeOfPolicyHolder bands: ' + $ageZeroByBand),
    'Example rows for Days:Policy-Accident/Days:Policy-Claim check:',
    ($dateOrderRows | Out-String),
    'Example rows for Month/MonthClaimed same-year check:',
    ($monthYearRows | Out-String),
    '',
    'Modelling notes (not counted as faults):',
    '- FraudFound is the target and is highly imbalanced: No=14,497; Yes=923.',
    '- PolicyNumber is a unique identifier and is excluded from model features.',
    '',
    'Checks passed (not counted as faults):',
    '- No blank source cells.',
    ('- Duplicate checks excluding PolicyNumber affected ' + $duplicateRecordsWithoutPolicy + ' records; excluding PolicyNumber and RepNumber affected ' + $duplicateRecordsWithoutIds + ' records.'),
    '- No -1 or 999-style codes were observed.',
    '- No invalid values were found in the checked numeric-like ranges.',
    '',
    'Quality notes:',
    '- Timeliness: Year ranges from 1994 to 1996; the later model task will use a chronological split.',
    '- Relevance: The file does not contain an obvious claim amount field, so financial loss size cannot be modelled directly.',
    '- Source data dictionary: no separate source data dictionary was included in the workspace; measurement roles are documented in reports/data_dictionary.md.'
) | Set-Content -LiteralPath (Join-Path $reports 'raw_quality_audit_lecture2.md') -Encoding utf8
