Attribute VB_Name = "Module1"
' ***************************************************************
' Project: SSD Market Price & Inventory Auditor
' Purpose: Identifies price drops and stock availability
'          to assist in procurement decisions.
' ***************************************************************

Sub AuditSSDMarket()
    Dim ws As Worksheet
    Dim lastRow As Long
    Dim i As Long
    Dim livePrice As Double
    Dim originalPrice As Double
    Dim dealCount As Integer
    
    Set ws = ThisWorkbook.Sheets(1) ' Focuses on the first sheet
    lastRow = ws.Cells(ws.Rows.Count, "B").End(xlUp).Row
    dealCount = 0
    
    ' Loop starts at Row 2 (assuming Row 1 is the header)
    For i = 2 To lastRow
        ' Convert currency strings to numbers for comparison
        ' We use Val() and Mid() to skip the "$" symbol
        livePrice = Val(Mid(ws.Cells(i, 3).Value, 2))
        originalPrice = Val(Mid(ws.Cells(i, 4).Value, 2))
        
        ' Logic: If Live Price is lower than Original Price, it's a deal!
        If livePrice < originalPrice And livePrice > 0 Then
            ' Highlight deal in Green
            ws.Range(ws.Cells(i, 1), ws.Cells(i, 8)).Interior.Color = RGB(200, 255, 200)
            dealCount = dealCount + 1
        Else
            ws.Range(ws.Cells(i, 1), ws.Cells(i, 8)).Interior.ColorIndex = xlNone
        End If
    Next i
    
    MsgBox "Audit Complete. Found " & dealCount & " active price drops!", vbInformation, "SSD Market Master"
End Sub
