library(jsonlite)
library(RCurl)


### Settings ===================================================

  # The url below pulls up K562 ChIP-seq data of interest from ENCODE

  args <- commandArgs(trailingOnly = TRUE)
  encode.experiment.links <- args[1]
  output.file.samples <- paste(args[2],'samples.tsv',sep="/")
  output.file.libraries <- paste(args[2],'libraries.tsv',sep="/")
  output.file.sequencings <-paste(args[2],'sequencings.tsv',sep="/") 
  
  acceptable.species <- c("human", "mouse", "rat", "cattle")  
  cell.labels <- c("cell line", "primary cell", "in vitro differentiated cells")
  tissue.labels <- c("tissue")
  experiment.types <- c("ATAC-seq",
                        "ChIP-seq")
  
  download.link.prefix <- "https://www.encodeproject.org/files/"
  
### GET METADATA FROM ENCODE DCC ===================================================
  # I use the jsonlite package to query the json format metadata at DCC. 
  # I imagine that users could input a URL like that links directly to their sample(s) of interst. (we should prob do a quick check to make sure that they don;t accidently put a URL that has 1000s of samples! Maybe we cap at 20. If they need more that can use multiple request)

  json <- fromJSON(encode.experiment.links)

  # The first thing I  extract is the experiment  metadata. 
  #We don't have an experiment object in out LIMS, but bascially it is a way to link together different biological replicates (for example, 2 replicates of H3K27ac from K562)
  exp.list.in<-json[["@graph"]]
  exp.list.in$biosample_ontology <- unlist(exp.list.in$biosample_ontology)

  # We still need to extract more metadata about the biosamples, replicates, and sequncing files from these experiments of interest
  # First, biosamples.... ================================

    # initialize table with the sample columns as LIMS template:samples
    template.samples <- as.data.frame(matrix(nrow=0, ncol=25))
    colnames(template.samples)<-c("Date",
                                  "PI",
                                  "Research contact name",
                                  "Research contact e-mail",
                                  "Research contact phone",
                                  "Fiscal contact name",
                                  "Fiscal conact e-mail",
                                  "Index for payment",
                                  "Sample ID",
                                  "Sample description",
                                  "Species",
                                  "Sample type",
                                  "Preperation",
                                  "Fixation?",
                                  "Sample amount",
                                  "Units",
                                  "Service requested",
                                  "Sequencing depth to target",
                                  "Sequencing length requested",
                                  "Sequencing type requested",
                                  "Notes",
                                  "Date sample received",
                                  "Initials of reciever",
                                  "Storage location",
                                  "Internal Notes")
    
    # loop through the experiments to extract biosample info
    # Note that one experiment may have multiple samples because it consists of multiple replicates
    biosample.list <- c()
    for(i in seq(exp.list.in$accession)){
      biosample.list <- c(biosample.list, exp.list.in$replicates[[i]]$library$biosample$accession)
    }
    biosample.list <- unique(biosample.list)
    
    for(b in seq(biosample.list)){
      template.samples[nrow(template.samples)+1,] <- NA
      temp.json<-fromJSON(paste("https://www.encodeproject.org/", biosample.list[b], "/?frame=embedded", sep = ""))
      #add sample ID
      template.samples$`Sample ID`[nrow(template.samples)] <- paste(temp.json$biosample_ontology$term_name, biosample.list[b], sep="_")
      #add sample description
      template.samples$`Sample description`[nrow(template.samples)] <- temp.json$summary
      #add species (only handle human and mouse for now)
      temp.species <- temp.json$organism$name
      if(temp.species %in% acceptable.species){
        template.samples$Species[nrow(template.samples)] <- temp.species
      } else {
        stop("incompatible species!")
      }
      #add sample type (only handle cells and tissue for now)
      temp.type <- temp.json$biosample_ontology$classification
      if(temp.type %in% cell.labels){
        template.samples$`Sample type`[nrow(template.samples)] <- "cultured cells"
      } else {
        if(temp.type %in% tissue.labels){
          template.samples$`Sample type`[nrow(template.samples)] <- "tissue"
        } else {
          stop("incompatible sample type!")
        }
      }
    }
    
    #add constant metadata
    template.samples$Date <- Sys.Date()
    template.samples$PI <- "Gorkin"
    template.samples$Notes <- "pseudosample, data downloaded from ENCODE"
    template.samples[,c("Preperation",
                        "Fixation?",
                        "Units",
                        "Service requested",
                        "Sequencing depth to target",
                        "Sequencing length requested",
                        "Sequencing type requested",
                        "Storage location")] <- "Other (please explain in notes)"
    
    # output sample table
    write.table(template.samples, output.file.samples, quote=F, row.names=F, sep="\t")
  
  # Next, libraries.... ================================
    
    template.libraries <- as.data.frame(matrix(nrow = 0, ncol=10))
    colnames(template.libraries)<-c("Sample ID (Must Match Column I in Sample Sheet)",
                                    "Library description",
                                    "Team member intials",
                                    "Date experiment started",
                                    "Date experiment completed",
                                    "Experiment type",
                                    "Protocol used",
                                    "Reference to notebook and page number",
                                    "Library ID (if library generated)",
                                    "Notes")
    
    library.list <- c()
    for(i in seq(exp.list.in$accession)){
      library.list <- c(library.list, exp.list.in$replicates[[i]]['@id'][,1])
    }
    library.list <- unique(library.list)
    for(l in seq(library.list)){
      template.libraries[nrow(template.libraries)+1,] <- NA
      temp.json<-fromJSON(paste("https://www.encodeproject.org/", library.list[l], "/?frame=embedded", sep = ""))
      #add sample ID
      template.libraries$`Sample ID (Must Match Column I in Sample Sheet)`[nrow(template.libraries)] <- 
        template.samples$`Sample ID`[grep(temp.json$library$biosample$accession, template.samples$`Sample ID`)]
      #add library description
      template.libraries$`Library description`[nrow(template.libraries)] <- paste("ENCODE", temp.json$experiment$description)
      #add experiment type
      temp.assay <- temp.json$experiment$assay_term_name
      if (temp.assay %in% experiment.types){
        template.libraries$`Experiment type`[nrow(template.libraries)] <- temp.json$experiment$assay_term_name
      } else{
        stop("incompatible experiment type")
      }
      #add library ID
      template.libraries$`Library ID (if library generated)`[nrow(template.libraries)] <- temp.json$libraries$accession
    }
    
    #add constant metadata
    template.libraries$Notes <- "pseudolibrary, ENCODE library downloaded from encodeproject.org"
    
    # output sample table
    write.table(template.libraries, output.file.libraries, quote=F, row.names=F, sep="\t")
      
  # Finally, sequencings... ================================
    
    template.seqs <- as.data.frame(matrix(nrow = 0, ncol=17))
    colnames(template.seqs) <- c("Sample ID (Must Match Column I in Sample Sheet)",
                                    "Label (for QC report)",
                                    "species",
                                    "Team member intials",
                                    "Date submitted for sequencing",
                                    "Library ID",
                                    "Sequencing ID",
                                    "Experiment type",
                                    "Sequening core",
                                    "Machine",
                                    "Sequening length",
                                    "Read type",
                                    "Portion of lane",
                                    "i7 index (if applicable)",
                                    "i5 Index (or single index)",
                                    "Notes",
                                    "file_download_URL(s)")
    
    temp.libs <- template.libraries$`Library ID (if library generated)`
    already.added <- c()
    for(l in seq(temp.libs)){
      temp.reps <- fromJSON(paste("https://www.encodeproject.org/", temp.libs[l], "/?frame=embedded", sep = ""))$replicates
      temp.sample.id <-  template.libraries$`Sample ID (Must Match Column I in Sample Sheet)`[l]
      for(r in seq(temp.reps)){
        temp.rep.info <- fromJSON(paste("https://www.encodeproject.org/", temp.reps[r], "/?frame=embedded", sep = ""))
        temp.target <- strsplit(strsplit(temp.rep.info$experiment$target, split="/")[[1]][3], split="-")[[1]][1]
        temp.files <- temp.rep.info$experiment$files
        for(f in seq(temp.files)){
          temp.json <- fromJSON(paste("https://www.encodeproject.org/",temp.files[f], "/?frame=embedded", sep = ""))
          if(temp.json$file_format=="fastq"){
            if(temp.json$library$accession==temp.libs[l] & !(temp.json$accession %in% already.added)){
              template.seqs[nrow(template.seqs)+1,] <- NA
              #add sample ID
              template.seqs$`Sample ID (Must Match Column I in Sample Sheet)`[nrow(template.seqs)] <- temp.sample.id
              #add label for report
              template.seqs$`Label (for QC report)`[nrow(template.seqs)] <-  paste(temp.sample.id, temp.target, temp.json$accession, sep="_")
              #add species 
              template.seqs$species[nrow(template.seqs)] <-  template.samples$Species[grep(temp.sample.id, template.samples$`Sample ID`)][1]
              #add lib ID
              template.seqs$`Library ID`[nrow(template.seqs)] <- temp.json$replicate$library$accession
              #add seq ID 
              template.seqs$`Sequencing ID`[nrow(template.seqs)]  <- paste(template.seqs$`Library ID`[nrow(template.seqs)], 
                                                                           temp.rep.info$technical_replicate_number, sep="_")
              #add experiment
              template.seqs$`Experiment type`[nrow(template.seqs)] <-  
                template.libraries$`Experiment type`[grep(temp.sample.id, template.libraries$`Sample ID (Must Match Column I in Sample Sheet)`)][1]
              #add seq length 
              template.seqs$`Sequening length`[nrow(template.seqs)] <-  temp.json$read_length
              #add read.type
              temp.read.type <- temp.json$run_type
              if(temp.read.type == "paired-ended"){
                template.seqs$`Read type`[nrow(template.seqs)] <- "PE"
              } else {
                template.seqs$`Read type`[nrow(template.seqs)] <- "SE"
              }
              #add notes
              temp.accessions <- temp.json$accession
              if(template.seqs$`Read type`[nrow(template.seqs)] == "PE"){
                temp.accessions <- c(temp.accessions, strsplit(temp.json$paired_with, split="/")[[1]][3])
              }
              template.seqs$Notes[nrow(template.seqs)] <- paste("ENCODE file accession(s)", paste(temp.accessions, collapse=","))
              already.added <- c(already.added, temp.accessions)
              #add download URL
              template.seqs$`file_download_URL(s)`[nrow(template.seqs)] <-
                paste(paste(download.link.prefix,temp.accessions,"/@@download/",temp.accessions,".fastq.gz",sep=""), collapse=",")
            }
          }
        }
      }
    }
    
    # output sample table
    write.table(template.seqs, output.file.sequencings, quote=F, row.names=F, sep="\t")
