use clap::{Arg, Command};
use serde::{Deserialize, Serialize};
use std::fs;
use syn::{visit::Visit, ItemFn, ItemStruct, ItemImpl, ItemTrait, Attribute, Visibility};
use syn::spanned::Spanned;

#[derive(Debug, Serialize, Deserialize)]
struct ParsedFunction {
    name: String,
    visibility: String,
    parameters: Vec<ParsedParameter>,
    return_type: Option<String>,
    attributes: Vec<String>,
    is_async: bool,
    is_unsafe: bool,
    line_start: usize,
    line_end: usize,
}

#[derive(Debug, Serialize, Deserialize)]
struct ParsedParameter {
    name: String,
    param_type: String,
    is_mutable: bool,
}

#[derive(Debug, Serialize, Deserialize)]
struct ParsedStruct {
    name: String,
    visibility: String,
    fields: Vec<ParsedField>,
    attributes: Vec<String>,
    line_start: usize,
    line_end: usize,
}

#[derive(Debug, Serialize, Deserialize)]
struct ParsedField {
    name: String,
    field_type: String,
    visibility: String,
}

#[derive(Debug, Serialize, Deserialize)]
struct ParsedTrait {
    name: String,
    visibility: String,
    methods: Vec<String>,
    attributes: Vec<String>,
    line_start: usize,
    line_end: usize,
}

#[derive(Debug, Serialize, Deserialize)]
struct ParsedImpl {
    target_type: String,
    trait_name: Option<String>,
    methods: Vec<String>,
    line_start: usize,
    line_end: usize,
}

#[derive(Debug, Serialize, Deserialize)]
struct ParsedUnsafeBlock {
    line_start: usize,
    line_end: usize,
    context: String,
}

#[derive(Debug, Serialize, Deserialize)]
struct ParseResult {
    functions: Vec<ParsedFunction>,
    structs: Vec<ParsedStruct>,
    traits: Vec<ParsedTrait>,
    impl_blocks: Vec<ParsedImpl>,
    unsafe_blocks: Vec<ParsedUnsafeBlock>,
    attributes: Vec<String>,
    uses: Vec<String>,
    contract_type: String,
    errors: Vec<String>,
}

struct RustVisitor {
    result: ParseResult,
}

impl RustVisitor {
    fn new(source: &str) -> Self {
        let mut visitor = Self {
            result: ParseResult {
                functions: Vec::new(),
                structs: Vec::new(),
                traits: Vec::new(),
                impl_blocks: Vec::new(),
                unsafe_blocks: Vec::new(),
                attributes: Vec::new(),
                uses: Vec::new(),
                contract_type: String::new(),
                errors: Vec::new(),
            },
        };
        visitor.detect_contract_type(source);
        visitor
    }

    fn extract_attributes(attrs: &[Attribute]) -> Vec<String> {
        attrs.iter()
            .map(|attr| quote::quote!(#attr).to_string())
            .collect()
    }

    fn visibility_to_string(vis: &Visibility) -> String {
        match vis {
            Visibility::Public(_) => "pub".to_string(),
            Visibility::Restricted(_) => "pub(restricted)".to_string(),
            Visibility::Inherited => "private".to_string(),
        }
    }

    fn get_line_numbers(&self, _span: proc_macro2::Span) -> (usize, usize) {
        // proc_macro2::Span doesn't provide line numbers in stable Rust
        // Return default values for now
        (1, 1)
    }

    fn detect_contract_type(&mut self, source: &str) {
        if source.contains("#[ink::contract]") || source.contains("ink_lang") {
            self.result.contract_type = "ink".to_string();
        } else if source.contains("cosmwasm_std") || source.contains("InstantiateMsg") {
            self.result.contract_type = "cosmwasm".to_string();
        } else if source.contains("anchor_lang") || source.contains("#[program]") {
            self.result.contract_type = "anchor".to_string();
        } else if source.contains("near_sdk") || source.contains("#[near_bindgen]") {
            self.result.contract_type = "near".to_string();
        } else {
            self.result.contract_type = "generic".to_string();
        }
    }
}

impl<'ast> Visit<'ast> for RustVisitor {
    fn visit_item_fn(&mut self, node: &'ast ItemFn) {
        let (line_start, line_end) = self.get_line_numbers(node.span());
        
        let parameters = node.sig.inputs.iter()
            .filter_map(|arg| {
                if let syn::FnArg::Typed(pat_type) = arg {
                    if let syn::Pat::Ident(pat_ident) = &*pat_type.pat {
                        return Some(ParsedParameter {
                            name: pat_ident.ident.to_string(),
                            param_type: quote::quote!(#pat_type.ty).to_string(),
                            is_mutable: pat_ident.mutability.is_some(),
                        });
                    }
                }
                None
            })
            .collect();

        let return_type = match &node.sig.output {
            syn::ReturnType::Default => None,
            syn::ReturnType::Type(_, ty) => Some(quote::quote!(#ty).to_string()),
        };

        let function = ParsedFunction {
            name: node.sig.ident.to_string(),
            visibility: Self::visibility_to_string(&node.vis),
            parameters,
            return_type,
            attributes: Self::extract_attributes(&node.attrs),
            is_async: node.sig.asyncness.is_some(),
            is_unsafe: node.sig.unsafety.is_some(),
            line_start,
            line_end,
        };

        self.result.functions.push(function);
        
        // Continue visiting
        syn::visit::visit_item_fn(self, node);
    }

    fn visit_item_struct(&mut self, node: &'ast ItemStruct) {
        let (line_start, line_end) = self.get_line_numbers(node.span());
        
        let fields = match &node.fields {
            syn::Fields::Named(fields) => {
                fields.named.iter()
                    .filter_map(|field| {
                        field.ident.as_ref().map(|ident| ParsedField {
                            name: ident.to_string(),
                            field_type: quote::quote!(#field.ty).to_string(),
                            visibility: Self::visibility_to_string(&field.vis),
                        })
                    })
                    .collect()
            }
            syn::Fields::Unnamed(fields) => {
                fields.unnamed.iter()
                    .enumerate()
                    .map(|(i, field)| ParsedField {
                        name: format!("field_{}", i),
                        field_type: quote::quote!(#field.ty).to_string(),
                        visibility: Self::visibility_to_string(&field.vis),
                    })
                    .collect()
            }
            syn::Fields::Unit => Vec::new(),
        };

        let struct_info = ParsedStruct {
            name: node.ident.to_string(),
            visibility: Self::visibility_to_string(&node.vis),
            fields,
            attributes: Self::extract_attributes(&node.attrs),
            line_start,
            line_end,
        };

        self.result.structs.push(struct_info);
        
        // Continue visiting
        syn::visit::visit_item_struct(self, node);
    }

    fn visit_item_trait(&mut self, node: &'ast ItemTrait) {
        let (line_start, line_end) = self.get_line_numbers(node.span());
        
        let methods = node.items.iter()
            .filter_map(|item| {
                if let syn::TraitItem::Fn(method) = item {
                    Some(method.sig.ident.to_string())
                } else {
                    None
                }
            })
            .collect();

        let trait_info = ParsedTrait {
            name: node.ident.to_string(),
            visibility: Self::visibility_to_string(&node.vis),
            methods,
            attributes: Self::extract_attributes(&node.attrs),
            line_start,
            line_end,
        };

        self.result.traits.push(trait_info);
        
        // Continue visiting
        syn::visit::visit_item_trait(self, node);
    }

    fn visit_item_impl(&mut self, node: &'ast ItemImpl) {
        let (line_start, line_end) = self.get_line_numbers(node.span());
        
        let target_type = quote::quote!(#node.self_ty).to_string();
        let trait_name = node.trait_.as_ref()
            .map(|(_, path, _)| quote::quote!(#path).to_string());
        
        let methods = node.items.iter()
            .filter_map(|item| {
                if let syn::ImplItem::Fn(method) = item {
                    Some(method.sig.ident.to_string())
                } else {
                    None
                }
            })
            .collect();

        let impl_info = ParsedImpl {
            target_type,
            trait_name,
            methods,
            line_start,
            line_end,
        };

        self.result.impl_blocks.push(impl_info);
        
        // Continue visiting
        syn::visit::visit_item_impl(self, node);
    }

    fn visit_item_use(&mut self, node: &'ast syn::ItemUse) {
        let use_statement = quote::quote!(#node).to_string();
        self.result.uses.push(use_statement);
        
        // Continue visiting
        syn::visit::visit_item_use(self, node);
    }

    fn visit_block(&mut self, node: &'ast syn::Block) {
        // Note: Unsafe blocks are handled differently in syn
        // They appear as ExprUnsafe expressions, not as Block unsafety

        // Continue visiting
        syn::visit::visit_block(self, node);
    }
}

fn parse_rust_file(file_path: &str) -> Result<ParseResult, Box<dyn std::error::Error>> {
    let source = fs::read_to_string(file_path)?;
    
    match syn::parse_file(&source) {
        Ok(ast) => {
            let mut visitor = RustVisitor::new(&source);
            visitor.detect_contract_type(&source);
            visitor.visit_file(&ast);
            Ok(visitor.result)
        }
        Err(e) => {
            let result = ParseResult {
                functions: Vec::new(),
                structs: Vec::new(),
                traits: Vec::new(),
                impl_blocks: Vec::new(),
                unsafe_blocks: Vec::new(),
                attributes: Vec::new(),
                uses: Vec::new(),
                contract_type: "unknown".to_string(),
                errors: vec![format!("Parse error: {}", e)],
            };
            Ok(result)
        }
    }
}

fn main() {
    let matches = Command::new("Rust Parser Helper")
        .version("0.1.0")
        .about("Parses Rust smart contracts using syn crate")
        .arg(
            Arg::new("file")
                .help("Rust file to parse")
                .required(true)
                .index(1),
        )
        .arg(
            Arg::new("output")
                .short('o')
                .long("output")
                .help("Output file for JSON result")
                .value_name("FILE"),
        )
        .get_matches();

    let file_path = matches.get_one::<String>("file").unwrap();
    
    match parse_rust_file(file_path) {
        Ok(result) => {
            let json_output = serde_json::to_string_pretty(&result).unwrap();
            
            if let Some(output_file) = matches.get_one::<String>("output") {
                if let Err(e) = fs::write(output_file, &json_output) {
                    eprintln!("Error writing to output file: {}", e);
                    std::process::exit(1);
                }
            } else {
                println!("{}", json_output);
            }
        }
        Err(e) => {
            eprintln!("Error parsing file: {}", e);
            std::process::exit(1);
        }
    }
}
