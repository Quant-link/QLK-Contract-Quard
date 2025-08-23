package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"go/ast"
	"go/parser"
	"go/token"
	"log"
	"os"
	"strings"
)

type ParsedFunction struct {
	Name        string            `json:"name"`
	Parameters  []ParsedParameter `json:"parameters"`
	ReturnTypes []string          `json:"return_types"`
	IsExported  bool              `json:"is_exported"`
	Receiver    *ParsedReceiver   `json:"receiver,omitempty"`
	LineStart   int               `json:"line_start"`
	LineEnd     int               `json:"line_end"`
}

type ParsedParameter struct {
	Name string `json:"name"`
	Type string `json:"type"`
}

type ParsedReceiver struct {
	Name string `json:"name"`
	Type string `json:"type"`
}

type ParsedStruct struct {
	Name       string        `json:"name"`
	Fields     []ParsedField `json:"fields"`
	IsExported bool          `json:"is_exported"`
	LineStart  int           `json:"line_start"`
	LineEnd    int           `json:"line_end"`
}

type ParsedField struct {
	Name       string `json:"name"`
	Type       string `json:"type"`
	IsExported bool   `json:"is_exported"`
	Tag        string `json:"tag,omitempty"`
}

type ParsedInterface struct {
	Name       string   `json:"name"`
	Methods    []string `json:"methods"`
	IsExported bool     `json:"is_exported"`
	LineStart  int      `json:"line_start"`
	LineEnd    int      `json:"line_end"`
}

type ParsedImport struct {
	Path  string `json:"path"`
	Name  string `json:"name,omitempty"`
	Alias string `json:"alias,omitempty"`
}

type ParsedGoroutine struct {
	FunctionCall string `json:"function_call"`
	LineStart    int    `json:"line_start"`
	Context      string `json:"context"`
}

type ParsedChannel struct {
	Name      string `json:"name"`
	Type      string `json:"type"`
	Direction string `json:"direction"` // "send", "receive", "bidirectional"
	LineStart int    `json:"line_start"`
}

type ParseResult struct {
	PackageName  string            `json:"package_name"`
	Functions    []ParsedFunction  `json:"functions"`
	Structs      []ParsedStruct    `json:"structs"`
	Interfaces   []ParsedInterface `json:"interfaces"`
	Imports      []ParsedImport    `json:"imports"`
	Goroutines   []ParsedGoroutine `json:"goroutines"`
	Channels     []ParsedChannel   `json:"channels"`
	ContractType string            `json:"contract_type"`
	Errors       []string          `json:"errors"`
}

type GoVisitor struct {
	fset   *token.FileSet
	result *ParseResult
	source string
}

func NewGoVisitor(fset *token.FileSet, source string) *GoVisitor {
	return &GoVisitor{
		fset:   fset,
		source: source,
		result: &ParseResult{
			Functions:  []ParsedFunction{},
			Structs:    []ParsedStruct{},
			Interfaces: []ParsedInterface{},
			Imports:    []ParsedImport{},
			Goroutines: []ParsedGoroutine{},
			Channels:   []ParsedChannel{},
			Errors:     []string{},
		},
	}
}

func (v *GoVisitor) Visit(node ast.Node) ast.Visitor {
	if node == nil {
		return nil
	}

	switch n := node.(type) {
	case *ast.File:
		v.result.PackageName = n.Name.Name
		v.detectContractType()

	case *ast.ImportSpec:
		v.visitImport(n)

	case *ast.FuncDecl:
		v.visitFunction(n)

	case *ast.GenDecl:
		v.visitGenDecl(n)

	case *ast.GoStmt:
		v.visitGoroutine(n)

	case *ast.CallExpr:
		v.visitCallExpr(n)
	}

	return v
}

func (v *GoVisitor) visitImport(imp *ast.ImportSpec) {
	parsed := ParsedImport{
		Path: strings.Trim(imp.Path.Value, `"`),
	}

	if imp.Name != nil {
		parsed.Name = imp.Name.Name
		if imp.Name.Name != "." && imp.Name.Name != "_" {
			parsed.Alias = imp.Name.Name
		}
	}

	v.result.Imports = append(v.result.Imports, parsed)
}

func (v *GoVisitor) visitFunction(fn *ast.FuncDecl) {
	pos := v.fset.Position(fn.Pos())
	end := v.fset.Position(fn.End())

	parsed := ParsedFunction{
		Name:        fn.Name.Name,
		Parameters:  []ParsedParameter{},
		ReturnTypes: []string{},
		IsExported:  ast.IsExported(fn.Name.Name),
		LineStart:   pos.Line,
		LineEnd:     end.Line,
	}

	// Parse receiver (for methods)
	if fn.Recv != nil && len(fn.Recv.List) > 0 {
		recv := fn.Recv.List[0]
		parsed.Receiver = &ParsedReceiver{
			Type: v.typeToString(recv.Type),
		}
		if len(recv.Names) > 0 {
			parsed.Receiver.Name = recv.Names[0].Name
		}
	}

	// Parse parameters
	if fn.Type.Params != nil {
		for _, param := range fn.Type.Params.List {
			paramType := v.typeToString(param.Type)
			if len(param.Names) > 0 {
				for _, name := range param.Names {
					parsed.Parameters = append(parsed.Parameters, ParsedParameter{
						Name: name.Name,
						Type: paramType,
					})
				}
			} else {
				parsed.Parameters = append(parsed.Parameters, ParsedParameter{
					Name: "",
					Type: paramType,
				})
			}
		}
	}

	// Parse return types
	if fn.Type.Results != nil {
		for _, result := range fn.Type.Results.List {
			parsed.ReturnTypes = append(parsed.ReturnTypes, v.typeToString(result.Type))
		}
	}

	v.result.Functions = append(v.result.Functions, parsed)
}

func (v *GoVisitor) visitGenDecl(gen *ast.GenDecl) {
	for _, spec := range gen.Specs {
		switch s := spec.(type) {
		case *ast.TypeSpec:
			v.visitTypeSpec(s)
		}
	}
}

func (v *GoVisitor) visitTypeSpec(ts *ast.TypeSpec) {
	pos := v.fset.Position(ts.Pos())
	end := v.fset.Position(ts.End())

	switch t := ts.Type.(type) {
	case *ast.StructType:
		v.visitStruct(ts.Name.Name, t, pos.Line, end.Line)
	case *ast.InterfaceType:
		v.visitInterface(ts.Name.Name, t, pos.Line, end.Line)
	}
}

func (v *GoVisitor) visitStruct(name string, st *ast.StructType, lineStart, lineEnd int) {
	parsed := ParsedStruct{
		Name:       name,
		Fields:     []ParsedField{},
		IsExported: ast.IsExported(name),
		LineStart:  lineStart,
		LineEnd:    lineEnd,
	}

	if st.Fields != nil {
		for _, field := range st.Fields.List {
			fieldType := v.typeToString(field.Type)
			tag := ""
			if field.Tag != nil {
				tag = field.Tag.Value
			}

			if len(field.Names) > 0 {
				for _, fieldName := range field.Names {
					parsed.Fields = append(parsed.Fields, ParsedField{
						Name:       fieldName.Name,
						Type:       fieldType,
						IsExported: ast.IsExported(fieldName.Name),
						Tag:        tag,
					})
				}
			} else {
				// Anonymous field
				parsed.Fields = append(parsed.Fields, ParsedField{
					Name:       "",
					Type:       fieldType,
					IsExported: false,
					Tag:        tag,
				})
			}
		}
	}

	v.result.Structs = append(v.result.Structs, parsed)
}

func (v *GoVisitor) visitInterface(name string, it *ast.InterfaceType, lineStart, lineEnd int) {
	parsed := ParsedInterface{
		Name:       name,
		Methods:    []string{},
		IsExported: ast.IsExported(name),
		LineStart:  lineStart,
		LineEnd:    lineEnd,
	}

	if it.Methods != nil {
		for _, method := range it.Methods.List {
			if len(method.Names) > 0 {
				for _, methodName := range method.Names {
					parsed.Methods = append(parsed.Methods, methodName.Name)
				}
			}
		}
	}

	v.result.Interfaces = append(v.result.Interfaces, parsed)
}

func (v *GoVisitor) visitGoroutine(gs *ast.GoStmt) {
	pos := v.fset.Position(gs.Pos())

	functionCall := ""
	if call, ok := gs.Call.Fun.(*ast.Ident); ok {
		functionCall = call.Name
	} else if sel, ok := gs.Call.Fun.(*ast.SelectorExpr); ok {
		functionCall = sel.Sel.Name
	}

	parsed := ParsedGoroutine{
		FunctionCall: functionCall,
		LineStart:    pos.Line,
		Context:      "goroutine",
	}

	v.result.Goroutines = append(v.result.Goroutines, parsed)
}

func (v *GoVisitor) visitCallExpr(ce *ast.CallExpr) {
	// Check for channel operations
	if ident, ok := ce.Fun.(*ast.Ident); ok {
		if ident.Name == "make" && len(ce.Args) > 0 {
			if chanType, ok := ce.Args[0].(*ast.ChanType); ok {
				pos := v.fset.Position(ce.Pos())

				direction := "bidirectional"
				if chanType.Dir == ast.SEND {
					direction = "send"
				} else if chanType.Dir == ast.RECV {
					direction = "receive"
				}

				parsed := ParsedChannel{
					Name:      "anonymous",
					Type:      v.typeToString(chanType.Value),
					Direction: direction,
					LineStart: pos.Line,
				}

				v.result.Channels = append(v.result.Channels, parsed)
			}
		}
	}
}

func (v *GoVisitor) typeToString(expr ast.Expr) string {
	switch t := expr.(type) {
	case *ast.Ident:
		return t.Name
	case *ast.SelectorExpr:
		return v.typeToString(t.X) + "." + t.Sel.Name
	case *ast.StarExpr:
		return "*" + v.typeToString(t.X)
	case *ast.ArrayType:
		if t.Len == nil {
			return "[]" + v.typeToString(t.Elt)
		}
		return "[...]" + v.typeToString(t.Elt)
	case *ast.ChanType:
		dir := ""
		if t.Dir == ast.SEND {
			dir = "chan<- "
		} else if t.Dir == ast.RECV {
			dir = "<-chan "
		} else {
			dir = "chan "
		}
		return dir + v.typeToString(t.Value)
	case *ast.MapType:
		return "map[" + v.typeToString(t.Key) + "]" + v.typeToString(t.Value)
	case *ast.InterfaceType:
		return "interface{}"
	case *ast.FuncType:
		return "func"
	default:
		return "unknown"
	}
}

func (v *GoVisitor) detectContractType() {
	source := strings.ToLower(v.source)

	if strings.Contains(source, "cosmos-sdk") || strings.Contains(source, "sdk.msg") {
		v.result.ContractType = "cosmos_sdk"
	} else if strings.Contains(source, "ethereum") || strings.Contains(source, "ethclient") {
		v.result.ContractType = "ethereum"
	} else if strings.Contains(source, "blockchain") || strings.Contains(source, "smart contract") {
		v.result.ContractType = "blockchain"
	} else {
		v.result.ContractType = "generic"
	}
}

func parseGoFile(filename string) (*ParseResult, error) {
	source, err := os.ReadFile(filename)
	if err != nil {
		return nil, fmt.Errorf("failed to read file: %v", err)
	}

	fset := token.NewFileSet()
	file, err := parser.ParseFile(fset, filename, source, parser.ParseComments)
	if err != nil {
		result := &ParseResult{
			PackageName: "unknown",
			Errors:      []string{fmt.Sprintf("Parse error: %v", err)},
		}
		return result, nil
	}

	visitor := NewGoVisitor(fset, string(source))
	ast.Walk(visitor, file)

	return visitor.result, nil
}

func main() {
	var filename = flag.String("file", "", "Go file to parse")
	var output = flag.String("output", "", "Output file for JSON result")
	flag.Parse()

	if *filename == "" {
		log.Fatal("Please provide a Go file to parse using -file flag")
	}

	result, err := parseGoFile(*filename)
	if err != nil {
		log.Fatalf("Error parsing file: %v", err)
	}

	jsonOutput, err := json.MarshalIndent(result, "", "  ")
	if err != nil {
		log.Fatalf("Error marshaling JSON: %v", err)
	}

	if *output != "" {
		err = os.WriteFile(*output, jsonOutput, 0644)
		if err != nil {
			log.Fatalf("Error writing output file: %v", err)
		}
	} else {
		fmt.Println(string(jsonOutput))
	}
}
